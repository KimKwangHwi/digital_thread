import asyncio
from datetime import datetime
import re
import os
import uuid
import logging
from src.repositories import MachineRepository, FileRepository, MachineLogRepository, RedisRepository
from src.schemas.machine import (
    MachineFileUploadResponse, MachineListResponse, MachineProgramStatusResponse, MachineInfo
)
from src.utils.exceptions import CustomException, ExceptionEnum
import logging

class MachineService:
    """
    CNC 장비와 연동되는 주요 비즈니스 로직(목록 조회, 파일 전송, 상태 추적 등)을 담당하는 서비스 계층.
    """

    def __init__(
        self, 
        machine_repo: MachineRepository, 
        file_repo: FileRepository, 
        log_repo: MachineLogRepository, 
        job_tracker: RedisRepository
    ):
        """
        :param machine_repo: 장비 관련 외부 API 통신 리포지토리
        :param file_repo: 파일(GridFS) 관리 리포지토리
        :param log_repo: MongoDB 가공 로그 관리 리포지토리
        :param job_tracker: Redis 기반 상태 추적기
        """
        self.machine_repo = machine_repo
        self.file_repo = file_repo
        self.log_repo = log_repo
        self.job_tracker = job_tracker

    async def get_machine_list(self) -> MachineListResponse:
        """
        현재 시스템에 등록된 모든 장비 정보를 반환.
        :return: MachineListResponse (장비 목록)
        """
        raw_list = await self.machine_repo.get_machine_list()
        machines = [MachineInfo(**item) for item in raw_list]
        return MachineListResponse(machines=machines)

    async def get_machine_data(self, endpoint: str, params: dict = None):
        """
        임의의 endpoint로부터 데이터를 조회합니다. LLM tool 호출 가능.
        
        :param endpoint: base_url 뒤에 붙는 경로 (예: "/machine/list")
        :param params: GET 요청에 사용할 쿼리 파라미터
        :return: 응답 데이터 value 또는 전체 json
        """
        return await self.machine_repo.get_data(endpoint, params)

    async def upload_torus_file(self, project_id: str, machine_id: int, file_id: str) -> MachineFileUploadResponse:
        """
        NC 파일을 장비로 업로드 (중복 파일 삭제, 폴더 생성, 포맷 검증 등 포함).
        :param project_id: 프로젝트 ID
        :param machine_id: 장비 ID
        :param file_id: 업로드할 NC 파일의 GridFS ID
        :return: 업로드 결과 정보
        """
        # 1. 파일 내용 로드 및 파일명 추출
        byte_io, filename = await self.file_repo.get_file_byteio_and_name(file_id)
        file_data = byte_io.read()
        # 2. NC 루트 경로 및 작업 폴더 경로 확보
        ncpath_root = await self.machine_repo.get_nc_root_path(machine_id)
        project_folder_path = f"{ncpath_root}OM/"
        await self.machine_repo.ensure_folder_exists(machine_id, project_folder_path)
        
        project_folder_path = project_folder_path + f"{project_id}/"

        # 3. 해당 장비 정보 확인
        machines: MachineListResponse = await self.get_machine_list()
        matched_machine = next((m for m in machines.machines if m.id == machine_id), None)
        if not matched_machine:
            raise CustomException(ExceptionEnum.MACHINE_NOT_FOUND)

        # 4. FANUC 계열인 경우 NC 파일명 포맷 검증
        if matched_machine.vendorCode.lower() == "fanuc":
            content_str = file_data.decode(errors="ignore")
            o_match = re.search(r"\bO(\d+)", content_str)
            if not o_match:
                raise CustomException(ExceptionEnum.INVALID_SIMENSE_FORMAT)
            o_number = f"O{o_match.group(1)}"
            if not filename.startswith(o_number):
                raise CustomException(ExceptionEnum.INVALID_FILE_NAME_FORMAT)

        # 5. 폴더 생성 및 동일 파일 삭제, 파일 업로드
        await self.machine_repo.ensure_folder_exists(machine_id, project_folder_path)
        await self.machine_repo.remove_file_if_exists(machine_id, project_folder_path, filename)
        await self.machine_repo.put_nc_file(machine_id, project_folder_path, filename, file_data)
        self.job_tracker.set_status(project_id, filename, machine_id, "가공 대기")

        return MachineFileUploadResponse(
            status=0,
            filename=filename,
            machine_id=machine_id,
            ncpath=project_folder_path
        )


    async def track_all_machines_forever(self):
        """
        모든 CNC 장비의 가공 상태를 백그라운드에서 지속적으로 추적.
        신규 장비가 추가되면 자동으로 트래킹을 시작.
        """
        tracked_machines = set()
        while True:
            machines = await self.get_machine_list()
            machine_ids = [m.id for m in machines.machines]
            logging.info(f"📡 Found {len(machine_ids)} machines: {machine_ids}")

            for machine_id in machine_ids:
                if machine_id not in tracked_machines:
                    tracked_machines.add(machine_id)
                    logging.info(f"🛰️ Starting tracking for machine {machine_id}")
                    asyncio.create_task(self._track_single_machine(machine_id))
            await asyncio.sleep(10)

    async def _track_single_machine(self, machine_id: int):
        """
        단일 CNC 장비의 가공 상태를 실시간 모니터링, 공구 교체, 로그 적재 및 상태 변경 처리.
        (내부에서만 사용)
        """
        current_tool = None
        operation_index = 1
        product_uuid = str(uuid.uuid4())
        log_doc = None
        is_processing = False
        current_project_id = None
        current_filename = None

        while True:
            try:
                status = await self.get_machine_status(machine_id)
                logging.info(f"🔍 Machine {machine_id} status = {status.programMode}")

                if status.programMode == 3:  # 가공 중
                    program_path = await self.machine_repo.get_current_program_name(machine_id)
                    dir_path = os.path.dirname(program_path) 
                    program_name = os.path.basename(program_path)
                    project_id = self.job_tracker.find_project_id_by_filename(program_name, machine_id)

                    if dir_path == "//CNC_MEM/USER/LIBRARY":
                        continue

                    if not project_id:
                        logging.warning(f"⚠️ No project found for {program_name} on machine {machine_id}")
                        await asyncio.sleep(3)
                        continue

                    self.job_tracker.mark_processing(project_id, program_name, machine_id)
                    tool = await self.machine_repo.get_active_tool_number(machine_id)

                    if not is_processing:
                        # 가공 시작 시 로그 초기화
                        is_processing = True
                        current_tool = tool
                        current_project_id = project_id
                        current_filename = program_name
                        log_doc = {
                            "project_id": project_id,
                            "machine_id": machine_id,
                            "product_uuid": product_uuid,
                            "start_time": datetime.now(),
                            "finish_time": None,
                            "finished": False,
                            "operations": []
                        }
                        await self._log_product_operation(log_doc, operation_index, current_tool, "start")
                    elif tool != current_tool:
                        # 공구 변경 감지 시 이전 공구 종료 + 새 공구 시작
                        await self._log_product_operation(log_doc, operation_index, current_tool, "end")
                        operation_index += 1
                        await self._log_product_operation(log_doc, operation_index, tool, "start")
                        current_tool = tool

                elif is_processing:
                    # 가공 종료 시 상태 및 로그 정리
                    self.job_tracker.mark_finished(current_project_id, current_filename, machine_id)
                    logging.info(f"🏁 Finished: {current_filename} on machine {machine_id}")
                    await self._log_product_operation(log_doc, operation_index, current_tool, "end")
                    log_doc["finish_time"] = datetime.now()
                    log_doc["finished"] = True
                    await self.log_repo.insert_log(log_doc)
                    # 상태 초기화
                    product_uuid = str(uuid.uuid4())
                    is_processing = False
                    log_doc = None
                    current_project_id = None
                    current_filename = None

            except Exception as e:
                logging.error(f"❌ Error tracking machine {machine_id}: {e}", exc_info=True)
            await asyncio.sleep(3)

    async def _log_product_operation(self, log_doc: dict, index: int, tool_number: int, action: str):
        """
        가공/공구 로그를 기록 (operation 배열에 추가/수정).
        :param log_doc: 현재 가공 로그 dict
        :param index: operation index
        :param tool_number: 공구 번호
        :param action: 'start' or 'end'
        """
        if action == "start":
            operation = {
                "uuid": str(uuid.uuid4()),
                "index": index,
                "toolNumber": tool_number,
                "start_time": datetime.now(),
                "end_time": None
            }
            log_doc["operations"].append(operation)
        elif action == "end":
            for op in reversed(log_doc["operations"]):
                if op["index"] == index and op["end_time"] is None:
                    op["end_time"] = datetime.now()
                    break
 

    async def match_category(self, category:str, endpoint: str, params: dict = None):
        """
        사용자 질문에서 카테고리를 추출하고 해당 카테고리에 맞는 파일을 읽고 엔드포인트 및 파라미터를 생성 후 API 호출의 반환값을 리턴합니다.
        1. 카테고리 매칭
        사용자의 질문을 기반으로 카테고리를 결정합니다. 반드시 13개의 속성 중 하나여야 합니다. 
        2. 엔드포인트 및 파라미터 설정
        결정된 카테고리에 따라 API 엔드포인트와 쿼리 파라미터를 설정합니다. 조건문으로 카테고리별로 분기합니다.
        
        :param category: 사용자 질문에서 추출한 카테고리. 다음 13개의 속성 중 하나입니다. 
            - machine
            - channel
            - activeTool
            - alarmORVariable
            - axis
            - buffer
            - currentProgram
            - feed
            - plc
            - spindle
            - toolArea
            - workOffset
            - workStatus
        :param endpoint: base_url 뒤에 붙는 경로 (예: "/machine/list")
        :param params: GET 요청에 사용할 쿼리 파라미터
        :return: 응답 데이터 value 또는 전체 json
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        manual_dir_path = os.path.join(current_dir, '..', 'torus_manual')
        file_name = "{}.json".format(category)
        
        
        return await self.machine_repo.get_data(endpoint, params)
        
        
        
    
    
    