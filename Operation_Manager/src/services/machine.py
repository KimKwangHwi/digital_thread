import asyncio
from datetime import datetime
import re
from typing import Dict
from typing import List
import os
from pathlib import Path
import uuid
import json
import logging
from src.repositories import MachineRepository, FileRepository, MachineLogRepository, RedisRepository
from src.schemas.machine import (
    MachineFileUploadResponse, MachineListResponse, MachineProgramStatusResponse, MachineInfo
)
from src.utils.exceptions import CustomException, ExceptionEnum
import logging

from langchain_huggingface import HuggingFaceEmbeddings
import pickle
import aiofiles

ERROR_STATUS_FILE_PATH = Path(__file__).resolve().parent.parent / "error_status.json"

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
 

    # ======================================================================
    
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
        장비의 상태 및 기본 정보를 조회합니다.

        endpoint 형식:
        • 일반 정보: /machine/{leaf_node}
        • NC 메모리 정보: /machine/ncMemory/{leaf_node}

        필수 파라미터: machine=i  (i번째 장비)

        === 일반 장비 정보 ===
        • cncModel - 해당 장비에 탑재된 NC의 모델명(STRING)
        • numberOfChannels - 장비에서 사용 가능한 채널(계통)의 개수(INTEGER)
        • cncVendor - NC 제조사 코드 (1: FANUC, 2: SIEMENS, 3:CSCAM, 4: MITSUBISHI, 5: KCNC)(INTEGER)
        • ncLinkState - NC와의 통신 가능 여부(BOOLEAN)
        • currentAccessLevel - 프로그램/디렉토리 접근 권한 수준 (SIEMENS 전용). 1: 제조자, 2: 서비스, 3: 사용자, 4: 프로그래머(키 스위치 3), 5: 공인 전문가(키 스위치 2), 6: 숙련된 전문가(키 스위치 1), 7: 준 숙련 전문가(키 스위치 0)(INTEGER)
        • basicLengthUnit - 장비가 사용하는 기본 길이 단위 (0: Metric, 1: Inches, 4: user Define 등)(INTEGER)
        • machinePowerOnTime - 장비의 전원이 켜진 시간 (단위: 분)(REAL)
        • currentCncTime - 장비에 설정된 현재 시각 (형식: yyyy-MM-ddTHH:mm:ss)(STRING)
        • machineType - 장비의 타입 (0: 알 수 없음, 1: Milling, 2: Lathe)(INTEGER)

        === NC 메모리 정보 ===
        • ncMemory/totalCapacity - NC 메모리의 전체 용량 (단위: byte)(REAL)
        • ncMemory/usedCapacity - 사용 중인 NC 메모리 용량 (단위: byte)(REAL)
        • ncMemory/freeCapacity - NC 메모리의 남은 용량 (단위: byte)(REAL)
        • ncMemory/rootPath - NC 메모리의 기본(루트) 경로(STRING)

        예시:
        - endpoint="/machine/cncModel"
        - endpoint="/machine/ncMemory/freeCapacity"
        - params= {"machine": 1}
        """

        return await self.machine_repo.get_data(endpoint, params)
    

    async def get_channel_data(self, endpoint: str, params: dict = None):
        
        """
        계통 별로 기록되는 채널의 상태 정보를 조회합니다. 리스트 구조입니다.
    
        endpoint 형식: /machine/channel/{leaf_node}
        필수 파라미터: machine=i (i번째 장비), channel=j (j번째 채널)
    
        사용 가능한 leaf_node:
        • channelEnabled  - 해당 채널의 사용 가능 여부(BOOLEAN)
        • toolAreaNumber  - 해당 채널에서 사용 가능한 공구 영역의 식별 번호. 단계통 장비의 경우 디폴트로 1. FANUC에서는 공구 영역과 계통이 동일하기 때문에 channel과 toolArea가 같은 개념으로 사용. SIEMENS의 공구 영역의 개수는 계통 수와 동등하며, 공구 영역과 계통 간 1:다 관계가 성립.(INTEGER)  
        • numberOfAxes  - 해당 채널에서 사용 가능한 축의 개수(INTEGER)
        • numberOfSpindles  - 해당 채널에서 사용 가능한 스핀들의 개수.(INTEGER)
        • alarmStatus   - 채널의 알람 상태. 0: no alarm, 1: alarm, 2: alarm without stop, 3: alarm with stop, 4: Battery low, 5: FAN, 6: PS warning, 7: FSSB waring, 8: Insulate warning, 9: Encoder warning 10: PMC alarm(INTEGER)
        • numberOfAlarms   - 해당 채널에서 발생한 알람의 총 개수(INTEGER)  
        • operateMode   - 공작기계의 운전 모드 (0: JOG, 1: MDI, 2: MEMORY(AUTO), 3: ZRN, 4: MPG, 5: **** 6: EDIT, 7: HANDLE, 8: Teach in JOG, 9: Teach in HANDLE 10: INC·feed, 11: REFERENCE, 12: REMOTE, 13: JOG-REPOS, 14: MDI-REF.POINT, 15: MDI-TEACH IN, 16: MDI-TECH IN-REF.POINT, 17: AUTO-TECH IN-REF.POINT 18: STEP, 19:RAPID, 20: TAPE, 21: AUTO-TEACH IN-JOG, 22: JOG-REF)(INTEGER)
        • numberOfWorkOffsets   - 사용 가능한 공작물 좌표계의 개수(INTEGER)
        • ncState   - CNC의 작동 상태 (0: Reset, 1: Stop, 2: Hold, 3: Start, 4: MSTR, 5: Interrupted, 6: Pause)(INTEGER)
        • motionStatus   - 장비의 현재 모션 상태 (1: Motion, 2: Dwell, 3: Wait)(INTEGER)  
        • emergencyStatus   - 상태 여부 (0: Not emergency, 1: Emergency, 2: Reset, 3: Wait)(INTEGER)
   

        예시: endpoint="/machine/channel/channelEnabled", params={"machine": 1, "channel": 1}
        """

        return await self.machine_repo.get_data(endpoint, params)
    
    async def get_axis_data(self, endpoint: str, params: dict = None):
        
        """
        축 별 상태 정보를 조회합니다. 
    
        endpoint 형식: 
        • 일반 정보: /machine/channel/axis/{leaf_node}
        • 전력 정보: /machine/channel/axis/axisPower/{leaf_node}
        
        필수 파라미터: machine=i (i번째 장비), channel=j (j번째 채널), axis=k (k번째 축)
    
         === 일반 축 정보 leaf_node ===
        • machinePosition - 기계 좌표계 기준 현재 위치(REAL)
        • workPosition - 공작물 좌표계 기준 현재 위치(REAL)
        • distanceToGo - 지령 위치까지 남은 이동 거리(REAL)
        • relativePosition - 상대 좌표계 기준 현재 위치(REAL)
        • axisName - 절대 좌표계의 축 이름(STRING)
        • relativeAxisName - 상대 좌표계의 축 이름 (FANUC 전용)(STRING)
        • axisLoad - 축에 걸리는 부하(REAL)
        • axisFeed - 현재 축의 이송 속도(REAL)
        • axisLimitPlus - '+' 방향 최대 이동 한계값(REAL)
        • axisLimitMinus - '-' 방향 최대 이동 한계값(REAL)
        • workAreaLimitPlus - 작업 금지 영역 '+' 방향 한계값(REAL)
        • workAreaLimitMinus - 작업 금지 영역 '-' 방향 한계값(REAL)
        • workAreaLimitPlusEnabled - 작업 금지 영역 '+' 방향 활성화 여부(BOOLEAN)
        • workAreaLimitMinusEnabled - 작업 금지 영역 '-' 방향 활성화 여부(BOOLEAN)
        • axisEnabled - 해당 축의 사용 가능 여부(BOOLEAN)
        • interlockEnabled - 해당 축의 인터락 상태 여부(BOOLEAN)
        • constantSurfaceSpeedControlEnabled - 주속 일정 제어(CSS) 활성화 여부(BOOLEAN)
        • axisCurrent - 해당 축의 전류 정보(REAL)
        • machineOrigin - 기계 원점 좌표값(REAL)
        • axisTemperature - 해당 축의 온도 정보(REAL)
        
        === 축 전력 정보 ===  
        • axisPower/actualPowerConsumption - 실 소비 전력 적산값(REAL)
        • axisPower/powerConsumption - 소비 전력 적산값(REAL)
        • axisPower/regeneratedPower - 회생 전력 적산값(REAL)
    
        예시: endpoint="/machine/channel/axis/axisLoad", params={"machine": 1, "channel": 1, "axis": 1}
        """

        return await self.machine_repo.get_data(endpoint, params)
    


    async def get_spindle_data(self, endpoint: str, params: dict = None):
        
        """
        스핀들 별 상태 정보를 조회합니다.

        endpoint 형식:
        • 일반 정보: /machine/channel/spindle/{leaf_node}
        • RPM 정보: /machine/channel/spindle/rpm/{leaf_node}
        • 전력 정보: /machine/channel/spindle/spindlePower/{leaf_node}

        필수 파라미터: machine=i, channel=j, spindle=k(k번째 스핀들)

        === 일반 스핀들 정보 ===
        • spindleLoad - 스핀들에 걸리는 부하(REAL)
        • spindleOverride - 스핀들 속도 오버라이드 비율(REAL)
        • spindleLimit - 최대 회전 속도 한계값(REAL)
        • spindleEnabled - 해당 스핀들의 사용 가능 여부(BOOLEAN)
        • spindleCurrent - 해당 스핀들의 전류 정보(REAL)
        • spindleTemperature - 해당 스핀들의 온도 정보(REAL)

        === 스핀들 RPM 정보 ===
        • rpm/commandedSpeed - 지령된 스핀들 회전 속도(REAL)
        • rpm/actualSpeed - 실제 측정된 스핀들 회전 속도(REAL)
        • rpm/speedUnit - 속도 단위 (0: mm/min, 1: inch/min, 2: rpm, 3: mm/rev, 4: inch/rev 등)(INTEGER)

        === 스핀들 전력 정보 ===
        • spindlePower/actualPowerConsumption - 실 소비 전력의 적산값(REAL)
        • spindlePower/powerConsumption - 소비 전력의 적산값(REAL)
        • spindlePower/regeneratedPower - 회생 전력의 적산값(REAL)

        예시:
        - endpoint="/machine/channel/spindle/spindleLoad"
        - endpoint="/machine/channel/spindle/rpm/actualSpeed"
        - endpoint="/machine/channel/spindle/spindlePower/powerConsumption"
        - params={"machine": 1, "channel": 1, "spindle": 1}
        """

        return await self.machine_repo.get_data(endpoint, params)

    
    async def get_feed_data(self, endpoint: str, params: dict = None):
        
        """
        축 이송 관련 정보를 조회합니다.

        endpoint 형식:
        • 오버라이드 정보: /machine/channel/feed/{leaf_node}
        • 이송 속도 정보: /machine/channel/feed/feedRate/{leaf_node}

        필수 파라미터: machine=i (i번째 장비), channel=j (j번째 채널)

        === 이송 오버라이드 정보 ===
        • feedOverride - 가공 이송 속도 오버라이드 비율(REAL)
        • rapidOverride - 급속 이송 속도 오버라이드 비율(REAL)

        === 이송 속도 정보 ===
        • feedRate/commandedSpeed - 지령된 이송 속도(REAL)
        • feedRate/actualSpeed - 실제 측정된 이송 속도(REAL)
        • feedRate/speedUnit - 속도 단위  (0: mm/min, 1: inch/min, 2: rpm, 3: mm/rev, 4: inch/rev 등)(INTEGER)

        예시:
        - endpoint="/machine/channel/feed/feedOverride"
        - endpoint="/machine/channel/feed/feedRate/actualSpeed"
        - params={"machine": 1, "channel": 1}
        """

        return await self.machine_repo.get_data(endpoint, params)
    
    
    async def get_workStatus_data(self, endpoint: str, params: dict = None):
        
        """
        가공 작업의 진척 상태 정보를 조회합니다.

        endpoint 형식:
        • 가공 수량 정보: /machine/channel/workStatus/workCounter/{leaf_node}
        • 가공 시간 정보: /machine/channel/workStatus/machiningTime/{leaf_node}

        필수 파라미터: machine=i, channel=j, workStatus=k (k번째 작업물)

        === 가공 수량 정보 ===
        • workCounter/currentWorkCounter - 현재까지 가공한 수량(INTEGER)
        • workCounter/targetWorkCounter - 목표 가공 수량(INTEGER)
        • workCounter/totalWorkCounter - 총 가공 수량(INTEGER)

        === 가공 시간 정보 ===
        • machiningTime/processingMachiningTime - 현재 가공이 진행된 시간 (단위: 초)(REAL)
        • machiningTime/estimatedMachiningTime - 예상 남은 가공 완료 시간 (SIEMENS 전용)(REAL)
        • machiningTime/machineOperationTime - 자동 운전 모드에서의 총 운전 시간 (단위: 초)(REAL)
        • machiningTime/actualCuttingTime - 실제 총 절삭 시간 (단위: 초)(REAL)

        예시:
        - endpoint="/machine/channel/workStatus/workCounter/currentWorkCounter"
        - endpoint="/machine/channel/workStatus/machiningTime/processingMachiningTime"
        - params={"machine": 1, "channel": 1}

        """

        return await self.machine_repo.get_data(endpoint, params)
    
    
    async def get_activeTool_data(self, endpoint: str, params: dict = None):
        
        """
        현재 활성화된 공구의 상세 정보를 조회합니다.

        endpoint 형식:
        • 일반 정보: /machine/channel/activeTool/{leaf_node}
        • 공구 날 정보: /machine/channel/activeTool/toolEdge/{leaf_node}
        • 공구 수명 정보: /machine/channel/activeTool/toolEdge/toolLife/{leaf_node}

        필수 파라미터: machine=i, channel=j

        === 일반 공구 정보 ===
        • locationNumber - 공구가 매거진에 탑재된 위치 번호(INTEGER)
        • toolName - 공구 이름(STRING)
        • toolNumber - 공구 식별 번호 (T 코드)(INTEGER)
        • numberOfEdges - 공구 날의 총 개수(INTEGER)
        • toolEnabled - 공구 영역 등록 및 매거진 탑재 여부 0: 공구 영역 미등록, 매거진 미탑재 상태, 1: 공구 영역 등록, 매거진 미탑재 상태, 2: 공구 영역 등록, 매거진 탑재 상태(INTEGER)
        • magazineNumber - 공구가 탑재된 매거진 번호(INTEGER)
        • sisterToolNumber - 할당된 대체 공구 번호(INTEGER)
        • toolLifeUnit - 공구 수명 측정 단위 기준.  0: no unit, 1: time, 2: count, 4: wear, 5: count(장착) 6: count(사용), 8: offset (INTEGER)
        • toolGroupNumber - 공구가 참조된 공구 그룹 번호 리스트(INTEGER)
        • toolUseOrderNumber - 그룹 내 공구 사용 순서 (FANUC 전용)(INTEGER)
        • toolStatus - 공구의 사용 상태 0 : Not enabled, 1 : Active tool, 2 : Enabled, 4 : Disabled, 8 : Measured, 9: 미사용 공구, 10 : 정상 수명 공구, 11 : Tool data is available (using), 12 : This tool is registered (available), 13 : This tool has expired, 14 : This tool was skipped, 16 : Prewarning limit reached , 32 : Tool being changed , 64 : Fixed location coded, 128 : Tool was in use , 256 : Tool is in the buffer magazine with transport order, 512 : Ignore disabled state of tool, 1024 : Tool must be unloaded, 2048 : Tool must be loaded, 4096 : Tool is a master tool, 8192 : Reserved, 16384 : Tool is marked for 1:1 exchange, 32768 : Tool is being used as a manual tool (INTEGER)

        === 공구 날(Edge) 정보 ===
        • toolEdge/edgeNumber - 공구 날 식별 번호(INTEGER)
        • toolEdge/toolType - 공구 유형 0: Not defined, 10: General-purpose tool, 11: Threading tool (Siemens에서는 540), 12: Grooving tool, 13: Round-nose tool, 14: Point nose straight tool, 15: Versatile tool, 20: Drill, 21: Counter sink tool, 22: Flat end mill, 23: Ball end mill, 24: Tap (Siemens에서는 240), 25: Reamer, 26: Boring tool, 27: Face mill, 50: Radius end mill, 51: 면취, 52: 선삭, 53: 홈삽입, 54: 나사절삭, 55: 선삭드릴, 56: 선삭탭, 100: Milling tool, 110: Ball nose end mill, 111: Conical ball end, 120: End mill, 121: End mill corner rounding, 130: Angle head cutter, 131: Corner rounding angle head cutter, 140: Facing tool, 145: Thread cutter, 150: Side mill, 151: Saw, 155: Bevelled cutter, 156: Bevelled cutter corner, 157: Tap. die-sink. cutter, 160: Drill&thread cut., 200: Twist drill, 205: Solid drill, 210: Boring bar, 220: Center drill, 230: Countersink, 231: Counterbore, 240: Tap, 241: Fine tap, 242: Tap, Whitworth, 250: Reamer, 500: Roughing tool, 510: Finishing tool, 520: Plunge cutter, 530: Cutting tool, 540: Threading tool, 550: Button tool, 560: Rotary drill, 580: 3D turning probe, 585: Calibrating tool, 700: Slotting saw, 710: 3D probe, 711: Edge finder, 712: Mono probe, 713: L probe, 714: Star probe, 725: Calibrating tool, 730: Stop, 731: Mandrel, 732: Steady rest, 900: Auxiliary tools(INTEGER)
        • toolEdge/lengthOffsetNumber - 공구 길이 보정 식별 번호(INTEGER)
        • toolEdge/geoLengthOffset - 공구 길이 X 보정값(REAL)
        • toolEdge/wearLengthOffset - 공구 길이 X 마모 보정값(REAL)
        • toolEdge/radiusOffsetNumber - 공구 반경 보정 식별 번호(INTEGER)
        • toolEdge/geoRadiusOffset - 공구 반경 보정값(REAL)
        • toolEdge/wearRadiusOffset - 공구 반경 마모 보정값(REAL)
        • toolEdge/edgeEnabled - 공구 날 사용 가능 여부(BOOLEAN)
        • toolEdge/geoLengthOffsetZ - 공구 길이 Z 보정값(REAL)
        • toolEdge/wearLengthOffsetZ - 공구 길이 Z 마모 보정값(REAL)
        • toolEdge/geoLengthOffsetY - 공구 길이 Y 보정값(REAL)
        • toolEdge/wearLengthOffsetY - 공구 길이 Y 마모 보정값(REAL)
        • toolEdge/geoOffsetNumber - 길이 X,Z, 반경의 식별 번호(INTEGER)
        • toolEdge/wearOffsetNumber - 길이 X,Z, 반경 마모값의 식별 번호(INTEGER)
        • toolEdge/cuttingEdgePosition - 공구 인선 방향(INTEGER)
        • toolEdge/tipAngle - 공구의 팁 각도(REAL)
        • toolEdge/holderAngle - 공구 홀더 각도(REAL)
        • toolEdge/insertAngle - 공구 인서트 각도(REAL)
        • toolEdge/insertWidth - 인선 너비 (SIEMENS 전용)(REAL)
        • toolEdge/insertLength - 인선 길이 (SIEMENS 전용)(REAL)
        • toolEdge/referenceDirectionHolderAngle - 홀더 각도 참조 방향 (SIEMENS 전용)(REAL)
        • toolEdge/directionOfSpindleRotation - 스핀들 회전 방향  0: 회전 없음, 1: 시계 방향, 2: 반시계 방향(SIEMENS 전용)(INTEGER)
        • toolEdge/numberOfTeeth - 공구 날 개수 (SIEMENS 전용)(INTEGER)
        
        === 공구 수명 정보 ===
        • toolEdge/toolLife/maxToolLife - 최대 공구 수명(REAL)
        • toolEdge/toolLife/restToolLife - 잔여 공구 수명(REAL)
        • toolEdge/toolLife/toolLifeCount - 현재 공구 사용량(REAL)
        • toolEdge/toolLife/toolLifeAlarm - 공구 수명 도달 경고 설정값 (SIEMENS 전용)(REAL)

        예시:
        - params = {"machine": 1, "channel": 1}
        - endpoint = "/machine/channel/activeTool/toolNumber"
        
        - params = {"machine": 1, "channel": 1}
        - endpoint = "/machine/channel/activeTool/toolEdge/geoLengthOffset"

        - params = {"machine": 1, "channel": 1}
        - endpoint = "/machine/channel/activeTool/toolEdge/toolLife/restToolLife"
        """

        return await self.machine_repo.get_data(endpoint, params)
    
    async def get_currentProgram_data(self, endpoint: str, params: dict = None):
        
        """
        현재 실행 중인 NC 프로그램의 상태 정보를 조회합니다.

        endpoint 형식:
        • 일반 정보: /machine/channel/currentProgram/{leaf_node}
        • 모달 정보: /machine/channel/currentProgram/modal/{leaf_node}
        • 실행 블록 정보: /machine/channel/currentProgram/overallBlock/{leaf_node}
        • 중단점 정보: /machine/channel/currentProgram/interruptBlock/{leaf_node}
        • 좌표계 오프셋 정보: /machine/channel/currentProgram/currentTotalWorkOffset/{leaf_node}
        • 현재 파일 정보: /machine/channel/currentProgram/currentFile/{leaf_node}
        • 메인 파일 정보: /machine/channel/currentProgram/mainFile/{leaf_node}
        • 제어 옵션 정보: /machine/channel/currentProgram/controlOption/{leaf_node}

        필수 파라미터: machine=i, channel=j 와 아래 각 항목별 파라미터

        === 일반 프로그램 정보 ===
        • sequenceNumber - 현재 실행 중인 시퀀스 번호(N 코드)(INTEGER)
        • currentBlockCounter - 실행 중인 블록 카운터(INTEGER)
        • lastBlock - 이전 블록 정보(STRING)
        • currentBlock - 현재 실행 중인 프로그램 블록 내용(STRING)
        • nextBlock - 다음 블록 정보(STRING)
        • activePartProgram - 실행 중인 프로그램 블록 정보(최대 200자)(STRING)
        • programMode - 프로그램 실행 모드  0: Reset, 1: Stop, 2: Hold, 3: Start(Active)(run), 4: MSTR, 5: Interrupted, 6: Pause, 7: Waiting (INTEGER)
        • currentWorkOffsetIndex - 현재 공작물 좌표계의 G 코드 인덱스(INTEGER)
        • currentWorkOffsetCode - 현재 공작물 좌표계의 G 코드 문자열(STRING)
        • currentDepthLevel - 현재 프로그램의 레벨 (메인, 서브루틴 등)(INTEGER)

        === G 코드 모달 정보 ===
        • modal/modalIndex - G 코드 인덱스 (필수 파라미터: modal=k. k번째 G 코드 인덱스)(INTEGER)
        • modal/modalCode - G 코드 문자열 (필수 파라미터: modal=k. k번째 G 코드 인덱스)(STRING)

        === 실행 블록 정보 (SIEMENS) ===
        • overallBlock/blockCounter - 블록 카운터 (필수 파라미터: overallBlock=k. k번째 프로그램 레벨)(INTEGER)
        • overallBlock/programName - 프로그램 이름 (필수 파라미터: overallBlock=k. k번째 프로그램 레벨)(STRING)

        === 중단점 블록 정보 (SIEMENS) ===
        • interruptBlock/depthLevel - 중단점 블록의 프로그램 레벨 (필수 파라미터: interruptBlock=k. k번째 프로그램 레벨)(INTEGER)
        • interruptBlock/blockCounter - 중단점 블록의 카운터 (필수 파라미터: interruptBlock=k. k번째 프로그램 레벨)(INTEGER)
        • interruptBlock/programName - 중단점 블록의 프로그램 이름 (필수 파라미터: interruptBlock=k. k번째 프로그램 레벨)(STRING)
        • interruptBlock/blockData - 중단점 블록 데이터 (필수 파라미터: interruptBlock=k. k번째 프로그램 레벨)(STRING)
        • interruptBlock/searchType - 중단점 검색 유형 (필수 파라미터: interruptBlock=k. k번째 프로그램 레벨)(INTEGER)
        • interruptBlock/mainProgramName - 중단점의 메인 프로그램 이름 (필수 파라미터 : interruptBlock=k. k번째 프로그램 레벨)(STRING)

        === 공작물 좌표계 오프셋 정보 ===
        • currentTotalWorkOffset/workOffsetIndex - G 코드 인덱스(INTEGER)
        • currentTotalWorkOffset/workOffsetValue - 축별 총 오프셋 값 (필수 파라미터 : workOffsetValue=k. k번째 축)(REAL)
        • currentTotalWorkOffset/workOffsetRotation - 축별 총 회전 오프셋 값 (필수 파라미터: workOffsetRotation=k. k번째 축)(REAL)
        • currentTotalWorkOffset/workOffsetScalingFactor - 축별 총 스케일링 값 (필수 파라미터: workOffsetScalingFactor=k. k번째 축)(REAL)
        • currentTotalWorkOffset/workOffsetMirroringEnabled - 축별 미러링 활성화 여부 (필수 파라미터: workOffsetMirroringEnabled=k. k번째 축)(BOOLEAN)

        === 현재 실행 파일 정보 ===
        • currentFile/programName - 파일명(STRING)
        • currentFile/programPath - 파일 경로(STRING)
        • currentFile/programSize - 파일 크기 (byte)(REAL)
        • currentFile/programDate - 파일 생성 날짜(STRING)
        • currentFile/programNameWithPath - 경로를 포함한 전체 파일명(STRING)

        === 메인 프로그램 파일 정보 ===
        • mainFile/programName - 파일명(STRING)
        • mainFile/programPath - 파일 경로(STRING)
        • mainFile/programSize - 파일 크기 (byte)(REAL)
        • mainFile/programDate - 파일 생성 날짜(STRING)
        • mainFile/programNameWithPath - 경로를 포함한 전체 파일명(STRING)
        
        === 프로그램 제어 옵션 정보 ===
        • controlOption/singleBlock - 싱글 블록 실행 여부(BOOLEAN)
        • controlOption/dryRun - 드라이 런 실행 여부(BOOLEAN)
        • controlOption/optionalStop - 옵셔널 스톱(M01) 활성화 여부(BOOLEAN)
        • controlOption/blockSkip - 블록 스킵 활성화 여부 리스트 (필수 파라미터: blockSkip=k. k번째 블록)(BOOLEAN)
        • controlOption/machineLock - 머신 락 활성화 여부(BOOLEAN)

        예시:
        - params = {"machine": 1, "channel": 1}
        - endpoint = "/machine/channel/currentProgram/sequenceNumber"

        - params = {"machine": 1, "channel": 1, "modal": 1}
        - endpoint = "/machine/channel/currentProgram/modal/modalCode"

        - params = {"machine": 1, "channel": 1, "workOffsetValue": 1}
        - endpoint = "/machine/channel/currentProgram/currentTotalWorkOffset/workOffsetValue"
        
        - params = {"machine": 1, "channel": 1, "blockSkip": 1}
        - endpoint = "/machine/channel/currentProgram/controlOption/blockSkip"
        """

        return await self.machine_repo.get_data(endpoint, params)
    
    
    async def get_workOffset_data(self, endpoint: str, params: dict = None):
        
        """
        공작물 좌표계(G54-G59)의 오프셋 정보를 조회합니다.

        endpoint 형식:
        • 오프셋 정보: /machine/channel/workOffset/{leaf_node}

        필수 파라미터: machine=i, channel=j, workOffset=k 와 아래 각 항목별 파라미터

        === 공작물 좌표계 오프셋 정보 ===
        • workOffsetValue - G 코드 인덱스에 대한 축별 오프셋 값 (필수 파라미터: workOffsetValue=l. l번째 축)(REAL)
        • workOffsetRotation - 축별 오프셋 회전량 (SIEMENS 전용) (필수 파라미터: workOffsetRotation=l. l번째 축)(REAL)
        • workOffsetScalingFactor - 축별 오프셋 확장량 (SIEMENS 전용) (필수 파라미터: workOffsetScalingFactor=l. l번째 축)(REAL)
        • workOffsetMirroringEnabled - 축별 미러링 활성화 여부 (SIEMENS 전용) (필수 파라미터: workOffsetMirroringEnabled=l. l번째 축)(BOOLEAN)
        • workOffsetFine - 축별 오프셋 Fine 값 (SIEMENS 전용) (필수 파라미터: workOffsetFine=l. l번째 축)(REAL)

        예시:
        # G54(workOffset=1) 좌표계의 1번째 축(workOffsetValue=1) 오프셋 값을 조회
        - params = {"machine": 1, "channel": 1, "workOffset": 1, "workOffsetValue": 1}
        - endpoint = "/machine/channel/workOffset/workOffsetValue"
        """

        return await self.machine_repo.get_data(endpoint, params)
    
    async def get_alarm_data(self, endpoint: str, params: dict = None):
        
        """
        발생한 알람 정보를 조회합니다.

        endpoint 형식:
        • 알람 정보: /machine/channel/alarm/{leaf_node}

        필수 파라미터: machine=i, channel=j, alarm=k(k번째 알람)

        === 알람 정보 ===
        • (수정하자) - 해당 계통에서 발생한 모든 알람에 대한 Text, Category, Number, raisedTimeStamp를 리스트로 나타내는 문자열(JSON 형태)(INTEGER)
        • alarmText - 알람 상세 내용 (STRING)
        • alarmCategory - 알람 유형 (STRING)
        • alarmNumber - 알람 번호 (STRING)
        • raisedTimeStamp - 알람 발생 시각 (STRING)

        

        예시:
        # 1번째 발생 알람의 상세 내용을 조회
        - params = {"machine": 1, "channel": 1, "alarm": 1}
        - endpoint = "/machine/channel/alarm/alarmText"
        """

        return await self.machine_repo.get_data(endpoint, params)
    
    async def get_variable_data(self, endpoint: str, params: dict = None):
        """
        사용자 변수(매크로) 정보를 조회합니다.
        
        
        === 사용자 변수 정보 ===
        • userVariable - 사용자 변수 값 (필수: variable=k. k번째 사용자 변수)(REAL)
        
        endpoint 형식: /machine/channel/variable/{leaf_node}
        """
    
    async def get_plc_data(self, endpoint: str, params: dict = None):
        
        """
        CNC 내부 PLC 메모리 데이터를 조회합니다.

        endpoint 형식:
        • 메모리 정보: /machine/pic/memory/{leaf_node}
        
        필수 파라미터: machine=i, channel=j

        필수 파라미터: machine=i 와 아래 각 항목별 주소 파라미터 {leaf_node}=j

        === PLC 메모리 정보 ===
        • rbitBlock - 읽기 전용 Bit 데이터 블록 (필수: rbitBlock=j. rbitBlock의 어드레스)(BOOLEAN)
        • bitBlock - 읽기/쓰기 가능 Bit 데이터 블록 (필수: bitBlock=j. bitBlock의 어드레스)(BOOLEAN)
        • rbyteBlock - 읽기 전용 Byte 데이터 블록 (필수: rbyteBlock=j. rbyteBlock의 어드레스)(BYTE)
        • byteBlock - 읽기/쓰기 가능 Byte 데이터 블록 (필수: byteBlock=j. byteBlock의 어드레스)(BYTE)
        • rwordBlock - 읽기 전용 Word(2byte) 데이터 블록 (필수: rwordBlock=j. rwordBlock의 어드레스)(WORD)
        • wordBlock - 읽기/쓰기 가능 Word(2byte) 데이터 블록 (필수: wordBlock=j. wordBlock의 어드레스)(WORD)
        • rdwordBlock - 읽기 전용 DWord(4byte) 데이터 블록 (필수: rdwordBlock=j. rdwordBlock의 어드레스)(DWORD)
        • dwordBlock - 읽기/쓰기 가능 DWord(4byte) 데이터 블록 (필수: dwordBlock=j. dwordBlock의 어드레스)(DWORD)
        • rqwordBlock - 읽기 전용 QWord(8byte) 데이터 블록 (필수: rqwordBlock=j. rqwordBlock의 어드레스)(QWORD)
        • qwordBlock - 읽기/쓰기 가능 QWord(8byte) 데이터 블록 (필수: qwordBlock=j. qwordBlock의 어드레스)(QWORD)

        예시:
        # 100번 주소의 읽기 전용 Bit 블록 값을 조회
        - params = {"machine": 1, "rbitBlock": 100}
        - endpoint = "/machine/pic/memory/rbitBlock"

        # 200번 주소의 읽기/쓰기 Word 블록 값을 조회
        - params = {"machine": 1, "wordBlock": 200}
        - endpoint = "/machine/pic/memory/wordBlock"
        """

        return await self.machine_repo.get_data(endpoint, params)
    
    async def get_toolArea_data(self, endpoint: str, params: dict = None):
        
        """
        장비의 공구 영역(매거진, 공구 목록) 정보를 조회합니다.

        endpoint 형식:
        • 일반 정보: /machine/toolArea/{leaf_node}
        • 매거진 정보: /machine/toolArea/magazine/{leaf_node}
        • T코드 기준 공구 정보: /machine/toolArea/tools/{leaf_node}
        • T코드 기준 공구 날 정보: /machine/toolArea/tools/toolEdge/{leaf_node}
        • T코드 기준 공구 수명 정보: /machine/toolArea/tools/toolEdge/toolLife/{leaf_node}
        • 등록순 기준 공구 정보: /machine/toolArea/registerTools/{leaf_node}
        • 등록순 기준 공구 날 정보: /machine/toolArea/registerTools/toolEdge/{leaf_node}
        • 등록순 기준 공구 수명 정보: /machine/toolArea/registerTools/toolEdge/toolLife/{leaf_node}

        필수 파라미터: machine=i, toolArea = j(j번째 공구 영역)  와 아래 각 항목별 파라미터가 계층적으로 필요합니다.
        (예: machine=i, toolArea=j, tools=k, toolEdge=l, {leaf_node}=m)
        ※ tools=k : 지정된 공구 번호 (k번째 공구)
        ※ registerTools=k : NC에 설정된 순서에 따른 인덱스 번호 (k번째 공구 인덱스 번호)
        

        === 일반 공구 영역 정보 ===
        • toolAreaEnabled - 해당 공구 영역 사용 가능 여부 (BOOLEAN)
        • numberOfMagazines - 사용 가능한 매거진 개수 (INTEGER)
        • numberOfRegisteredTools - 공구 영역에 등록된 총 공구 개수 (INTEGER)
        • numberOfLoadedTools - 매거진에 탑재된 총 공구 개수 (INTEGER)
        • numberOfToolGroups - 등록된 공구 그룹의 개수 (INTEGER)
        • numberOfToolOffsets - 등록된 공구 오프셋의 개수 (INTEGER)

        === 매거진 정보 ===
        • magazine/magazineEnabled - 해당 매거진 사용 가능 여부 (필수: magazine=k. k번째 매거진)(BOOLEAN)
        • magazine/magazineName - 매거진 이름 (SIEMENS 전용) (필수: magazine=k. k번째 매거진)(STRING)
        • magazine/numberOfRealLocations - 매거진의 물리적 포트(위치) 개수 (필수: magazine=k. k번째 매거진)(INTEGER)
        • magazine/magazinePhysicalNumber - 매거진의 물리적 번호 (필수: magazine=k. k번째 매거진)(INTEGER)
        • magazine/numberOfLoadedTools - 해당 매거진에 탑재된 공구 개수 (필수: magazine=k. k번째 매거진)(INTEGER)

        === 공구 상세 정보 (T코드: tools=k / 등록순: registerTools=k) ===
        # 아래 항목들은 tools와 registerTools 경로에서 동일하게 사용됩니다. (예: /machine/toolArea/tools/toolName)
        • locationNumber - 공구가 매거진에 탑재된 위치 번호 (필수: tools/registerTools=k)(INTEGER)
        • toolName - 공구 이름 (필수: tools/registerTools=k)(STRING)
        • numberOfEdges - 공구 날의 총 개수 (필수: tools/registerTools=k)(INTEGER)
        • toolEnabled - 공구 영역 등록 및 매거진 탑재 여부 0: 공구 영역 미등록, 매거진 미탑재 상태, 1: 공구 영역 등록, 매거진 미탑재 상태, 2: 공구 영역 등록, 매거진 탑재 상태(INTEGER) (필수: toolGroupNumber=l. l번째 공구 그룹)
        • magazineNumber - 공구가 탑재된 매거진 번호 (필수: tools/registerTools=k)(INTEGER)
        • sisterToolNumber - 할당된 대체 공구 번호 (필수: tools/registerTools=k)(INTEGER)
        • toolLifeUnit - 공구 수명 측정 단위 기준 (필수: tools/registerTools=k, toolLifeUnit=l)(INTEGER)
        • toolGroupNumber - 공구가 참조된 공구 그룹 번호 리스트 (필수: tools/registerTools=k)(LIST[INTEGER])
        • toolUseOrderNumber - 그룹 내 공구 사용 순서 (FANUC 전용) (필수: tools/registerTools=k)(INTEGER)
        • toolStatus - 공구의 사용 상태 0 : Not enabled, 1 : Active tool, 2 : Enabled, 4 : Disabled, 8 : Measured, 9: 미사용 공구, 10 : 정상 수명 공구, 11 : Tool data is available (using), 12 : This tool is registered (available), 13 : This tool has expired, 14 : This tool was skipped, 16 : Prewarning limit reached , 32 : Tool being changed , 64 : Fixed location coded, 128 : Tool was in use , 256 : Tool is in the buffer magazine with transport order, 512 : Ignore disabled state of tool, 1024 : Tool must be unloaded, 2048 : Tool must be loaded, 4096 : Tool is a master tool, 8192 : Reserved, 16384 : Tool is marked for 1:1 exchange, 32768 : Tool is being used as a manual tool (필수: tools/registerTools=k, toolStatus = l. l번째 공구 그룹)(INTEGER)

        === 공구 날(Edge) 상세 정보 ===
        # 아래 항목들은 .../tools/toolEdge 및 .../registerTools/toolEdge 경로에서 동일하게 사용됩니다.
        # 파라미터 예시: (필수: toolArea=j, tools=k, toolEdge=l)
        • toolType - 공구 유형 0: Not defined, 10: General-purpose tool, 11: Threading tool (Siemens에서는 540), 12: Grooving tool, 13: Round-nose tool, 14: Point nose straight tool, 15: Versatile tool, 20: Drill, 21: Counter sink tool, 22: Flat end mill, 23: Ball end mill, 24: Tap (Siemens에서는 240), 25: Reamer, 26: Boring tool, 27: Face mill, 50: Radius end mill, 51: 면취, 52: 선삭, 53: 홈삽입, 54: 나사절삭, 55: 선삭드릴, 56: 선삭탭, 100: Milling tool, 110: Ball nose end mill, 111: Conical ball end, 120: End mill, 121: End mill corner rounding, 130: Angle head cutter, 131: Corner rounding angle head cutter, 140: Facing tool, 145: Thread cutter, 150: Side mill, 151: Saw, 155: Bevelled cutter, 156: Bevelled cutter corner, 157: Tap. die-sink. cutter, 160: Drill&thread cut., 200: Twist drill, 205: Solid drill, 210: Boring bar, 220: Center drill, 230: Countersink, 231: Counterbore, 240: Tap, 241: Fine tap, 242: Tap, Whitworth, 250: Reamer, 500: Roughing tool, 510: Finishing tool, 520: Plunge cutter, 530: Cutting tool, 540: Threading tool, 550: Button tool, 560: Rotary drill, 580: 3D turning probe, 585: Calibrating tool, 700: Slotting saw, 710: 3D probe, 711: Edge finder, 712: Mono probe, 713: L probe, 714: Star probe, 725: Calibrating tool, 730: Stop, 731: Mandrel, 732: Steady rest, 900: Auxiliary tools (INTEGER) (INTEGER)
        • lengthOffsetNumber - 공구 길이 보정 식별 번호 (필수: lengthOffsetNumber=m. m번째 공구 그룹)(INTEGER)
        • toolEdge/lengthOffsetNumber - 공구 길이 보정 식별 번호 (필수: lengthOffsetNumber=m. m번째 공구 그룹)(INTEGER)
        • toolEdge/geoLengthOffset - 공구 길이 X 보정값 (필수: geoLengthOffset=m. m번째 공구 그룹)(REAL)
        • toolEdge/wearLengthOffset - 공구 길이 X 마모 보정값 (필수: wearLengthOffset=m. m번째 공구 그룹)(REAL)
        • toolEdge/radiusOffsetNumber - 공구 반경 보정 식별 번호 (필수: radiusOffsetNumber=m. m번째 공구 그룹)(INTEGER)
        • toolEdge/geoRadiusOffset - 공구 반경 보정값 (필수: geoRadiusOffset=m. m번째 공구 그룹)(REAL)
        • toolEdge/wearRadiusOffset - 공구 반경 마모 보정값 (필수: wearRadiusOffset=m. m번째 공구 그룹)(REAL)
        • toolEdge/edgeEnabled - 공구 날 사용 가능 여부 (BOOLEAN)
        • toolEdge/geoLengthOffsetZ - 공구 길이 Z 보정값 (필수: geoLengthOffsetZ=m. m번째 공구 그룹)(REAL)
        • toolEdge/wearLengthOffsetZ - 공구 길이 Z 마모 보정값 (필수: wearLengthOffsetZ=m. m번째 공구 그룹)(REAL)
        • toolEdge/geoLengthOffsetY - 공구 길이 Y 보정값 (필수: geoLengthOffsetY=m. m번째 공구 그룹)(REAL)
        • toolEdge/wearLengthOffsetY - 공구 길이 Y 마모 보정값 (필수: wearLengthOffsetY=m. m번째 공구 그룹)(REAL)
        • toolEdge/geoOffsetNumber - 길이 X,Z, 반경의 식별 번호 (필수: geoOffsetNumber=m. m번째 공구 그룹)(INTEGER)
        • toolEdge/wearOffsetNumber - 길이 X,Z, 반경 마모값의 식별 번호 (필수: wearOffsetNumber=m. m번째 공구 그룹)(INTEGER)
        • toolEdge/cuttingEdgePosition - 공구 인선 방향 (필수: cuttingEdgePosition=m. m번째 공구 그룹)(INTEGER)
        • toolEdge/tipAngle - 공구의 팁 각도 (REAL)
        • toolEdge/holderAngle - 공구 홀더 각도 (REAL)
        • toolEdge/insertAngle - 공구 인서트 각도 (REAL)
        • toolEdge/insertWidth - 인선 너비 (SIEMENS 전용) (REAL)
        • toolEdge/insertLength - 인선 길이 (SIEMENS 전용) (REAL)
        • toolEdge/referenceDirectionHolderAngle - 홀더 각도 참조 방향 (SIEMENS 전용) (REAL)
        • toolEdge/directionOfSpindleRotation - 스핀들 회전 방향 (SIEMENS 전용) (INTEGER)
        • toolEdge/numberOfTeeth - 공구 날 개수 (SIEMENS 전용) (INTEGER)

        === 공구 수명 상세 정보 ===
        # 아래 항목들은 .../toolEdge/toolLife 경로에서 동일하게 사용됩니다.
        # 파라미터 예시: (필수: machine = i, toolArea=j, tools=k, toolEdge=l)
        • toolLife/maxToolLife - 최대 공구 수명 (필수: maxToolLife=m)(REAL)
        • toolLife/restToolLife - 잔여 공구 수명 (필수: restToolLife=m)(REAL)
        • toolLife/toolLifeCount - 현재 공구 사용량 (필수: toolLifeCount=m)(REAL)
        • toolLife/toolLifeAlarm - 공구 수명 도달 경고 설정값 (REAL)

        예시:
        # 1번 공구 영역의 매거진 개수 조회
        - params = {"machine": 1, "toolArea": 1}
        - endpoint = "/machine/toolArea/numberOfMagazines"

        # T코드 5번 공구의 이름 조회
        - params = {"machine": 1, "toolArea": 1, "tools": 5}
        - endpoint = "/machine/toolArea/tools/toolName"

        # T코드 5번, 1번 날(Edge), 1번 그룹의 길이 X 보정값 조회
        - params = {"machine": 1, "toolArea": 1, "tools": 5, "toolEdge": 1, "geoLengthOffset": 1}
        - endpoint = "/machine/toolArea/tools/toolEdge/geoLengthOffset"
        
        # 등록순 3번 공구, 1번 날(Edge), 1번 그룹의 잔여 수명 조회
        - params = {"machine": 1, "toolArea": 1, "registerTools": 3, "toolEdge": 1, "restToolLife": 1}
        - endpoint = "/machine/toolArea/registerTools/toolEdge/toolLife/restToolLife"
        """

        return await self.machine_repo.get_data(endpoint, params)
    
    
    async def get_buffer_data(self, endpoint: str, params: dict = None):
        
        """
        내장 센서 데이터의 시계열 수집(Time-series) 정보를 조회합니다 (KCNC, FANUC만 지원).

        endpoint 형식:
        • 버퍼 정보: /machine/buffer/{leaf_node}
        • 스트림 정보: /machine/buffer/stream/{leaf_node}

        필수 파라미터: machine=i, buffer= j(j번째 버퍼) 와 아래 각 항목별 파라미터가 계층적으로 필요합니다.
        (예: machine=i, buffer=j, stream=k)

        === 버퍼 정보 ===
        • bufferEnabled - 해당 버퍼 사용 가능 여부 (BOOLEAN)
        • numberOfStream - 해당 버퍼의 최대 스트림 개수 (INTEGER)
        • statusOfStream - 스트림 상태 (0: 설정 가능, 1: 수집 가능, 2: 수집 대기, 3: 수집 중, 4: 수집 대기 혹은 수집 중, 5: 수집 완료/종료, -1: CNC 연결 실패, -2: 설정값 적용 실패 등)(필수: buffer=j) (INTEGER)
        • modOfStream - 스트림 수집 모드 (0: 반복 수집, 1: 1회 수집) (INTEGER)
        • machineChannelOfStream - 스트림 수집 시 사용할 채널(INTEGER)
        • periodOfStream - 1회 수집 기간 (단위: ms) (INTEGER)
        • triggerOfStream - 수집 시작 트리거 (0: 즉시, 1이상: 시퀀스 번호)(INTEGER)
        • frequencyOfStream - 모든 스트림에 공통으로 적용할 수집 주파수 (Hz)(INTEGER)

        === 스트림 채널 정보 ===
        • stream/streamEnabled - 해당 스트림 사용 가능 여부 (필수: stream=k. k번째 스트림)(BOOLEAN)
        • stream/streamFrequency - 해당 스트림의 수집 주파수 (Hz) (필수: stream=k. k번째 스트림)(INTEGER)
        • stream/streamCategory - 수집 대상 데이터 카테고리 (필수: stream=k. k번째 스트림)(INTEGER)
        • stream/streamSubcategory - 수집 대상 데이터 서브카테고리 (축/스핀들 번호 등) (필수: stream=k. k번째 스트림)(INTEGER)
        • stream/streamType - 수집 유형 (KCNC 전용) (필수: stream=k. k번째 스트림)(INTEGER)
        • stream/streamStartBit - 수집 유형이 Bit일 때 Start Bit (KCNC 전용) (필수: stream=k. k번째 스트림)(INTEGER)
        • stream/streamEndBit - 수집 유형이 Bit일 때 End Bit (KCNC 전용) (필수: stream=k. k번째 스트림)(INTEGER)
        • stream/value - 해당 스트림에서 마지막으로 수집된 데이터 값 (필수: stream=k. k번째 스트림)(REAL)

        예시:
        # 1번 버퍼의 수집 상태를 조회
        - params = {"machine": 1, "buffer": 1}
        - endpoint = "/machine/buffer/statusOfStream"

        # 1번 버퍼의 3번 스트림에서 마지막으로 수집된 값을 조회
        - params = {"machine": 1, "buffer": 1, "stream": 3}
        - endpoint = "/machine/buffer/stream/value"
        """

        return await self.machine_repo.get_data(endpoint, params)
    

    async def get_error_info_by_code(self, error_code: int) -> Dict[str, str]:
        """
        주어진 에러 코드(error_status)에 해당하는 분류와 설명을 반환합니다.

        Args:
            error_code (int): 조회할 9자리 에러 상태 코드.

        Returns:
            Dict[str, str]: '분류'와 '설명'이 포함된 딕셔너리.
                           에러 코드를 찾지 못하거나 파일이 없으면 에러 정보가 담긴 딕셔너리를 반환합니다.
        """
        # 입력된 정수형 에러 코드를 JSON 파일의 키 형식인 문자열로 변환합니다.
        error_code_str = str(error_code)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, '..', 'torus_manual/error_status.json')

        try:
            # UTF-8 인코딩으로 JSON 파일을 엽니다. (한글 포함)
            with open(json_file_path, 'r', encoding='utf-8') as f:
                error_data = json.load(f)

            # .get() 메소드를 사용하여 에러 코드를 찾습니다.
            # 키가 존재하지 않으면 None을 반환하여 KeyError를 방지합니다.
            error_info = error_data.get(error_code_str)

            if error_info:
                return error_info
            else:
                return {
                    "분류": "Not Found",
                    "설명": f"에러 코드 '{error_code}'에 해당하는 정보를 찾을 수 없습니다."
                }

        except FileNotFoundError:
            return {
                "분류": "File Error",
                "설명": f"에러 정의 파일({json_file_path})을 찾을 수 없습니다."
            }
        except json.JSONDecodeError:
            return {
                "분류": "JSON Error",
                "설명": "에러 정의 파일(error_status.json)의 형식이 올바르지 않습니다."
            }
        

    async def get_description_and_params_by_uri(self, endpoint: str):
        """
        주어진 API 엔드포인트에 대한 설명과 필수 파라미터를 반환합니다.

        직전 tool 호출의 결과로 error_status : 538992680가 반환된 경우,
        이 tool을 호출하여 해당 엔드포인트의 설명과 필수 파라미터를 확인한 후,
        직전에 호출한 tool에 재입력하여 다시 시도할 수 있습니다.

        Args:
            endpoint (str): API 엔드포인트.

        Returns:
            dict: 엔드포인트에 대한 설명 및 필수 파라미터를 포함하는 딕셔너리.
                오류가 발생하면 "__error__" 키를 포함한 딕셔너리를 반환합니다.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, '..', 'torus_manual/uri_params.json')

        try:
            # JSON 파일을 비동기적으로 읽기
            async with aiofiles.open(json_file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            api_data = json.loads(file_content)

            # 엔드포인트 정보 검색
            api_info = api_data.get(endpoint)

            # 결과 반환
            if api_info:
                return {
                    "description": api_info.get("description"),
                    "required_params": api_info.get("required_params")
                }
            else:
                # 정보를 찾지 못한 경우
                return {
                    "__error__": True,
                    "message": f"엔드포인트 '{endpoint}'에 대한 정보를 찾을 수 없습니다.",
                    "endpoint": endpoint,
                    "full_api_response": None
                }

        except FileNotFoundError:
            return {
                "__error__": True,
                "message": "URI 및 파라미터 JSON 파일을 찾을 수 없습니다. 경로를 확인하세요."
            }
        except json.JSONDecodeError:
            return {
                "__error__": True,
                "message": "URI 및 파라미터 JSON 파일의 형식이 잘못되었습니다."
            }
        except Exception as e:
            return {
            "__error__": True,
            "message": f"알 수 없는 오류가 발생했습니다: {str(e)}"
            }

    async def guardrail(self, query: str) :
        """
        - 사용자의 질문을 평가하여 도메인 관련성과 명확성을 확인합니다. 
        - 모호하거나 관련 없는 질문을 필터링하기 위해 다른 모든 툴보다 먼저 호출되어야 합니다.
        
        """
        
        
    async def get_toolLife_info(self, machine: int):
        """
        등록순 기준 공구 수명 정보를 비동기적으로 효율적이게 조회합니다. 장비 번호만 입력하면 됩니다.
        Args:
            machine (int): 조회할 장비 번호.
        """
        machine_param = {"machine": machine, "toolArea": 1}
        numberOfRegisteredTools = await self.machine_repo.get_data("/machine/toolArea/numberOfRegisteredTools", machine_param)

        if not (isinstance(numberOfRegisteredTools, int) and numberOfRegisteredTools > 0):
            # 유효한 공구 개수가 없으면 빈 리스트 또는 에러 메시지 반환
            return "등록된 공구가 없습니다."

        # 1. 모든 공구의 날(edge) 개수를 동시에 조회
        edge_tasks = []
        for i in range(1, numberOfRegisteredTools + 1):
            edge_params = machine_param.copy()
            edge_params["registerTools"] = i
            edge_tasks.append(
                self.machine_repo.get_data("/machine/toolArea/registerTools/numberOfEdges", edge_params)
            )
        numberOftoolEdgesList = await asyncio.gather(*edge_tasks)
        cleaned_edges_list = [n if isinstance(n, int) else 1 for n in numberOftoolEdgesList]
        # 2. 모든 공구의 모든 날에 대한 수명 정보 요청 태스크 생성
        life_info_tasks = []
        tool_name_tasks = []
        for i, num_edges in enumerate(cleaned_edges_list):
            tool_num = i + 1
            
            tool_name_tasks.append(self.machine_repo.get_data("/machine/toolArea/registerTools/toolName", {**machine_param, "registerTools": tool_num}))
            for j in range(1, num_edges + 1):
                base_params = {**machine_param, "registerTools": tool_num, "toolEdge": j}
                
                # 4가지 수명 정보 요청을 태스크 리스트에 추가
                life_info_tasks.append(self.machine_repo.get_data("/machine/toolArea/registerTools/toolEdge/toolLife/restToolLife", {**base_params, "restToolLife": 1}))
                life_info_tasks.append(self.machine_repo.get_data("/machine/toolArea/registerTools/toolEdge/toolLife/maxToolLife", {**base_params, "maxToolLife": 1}))
                life_info_tasks.append(self.machine_repo.get_data("/machine/toolArea/registerTools/toolEdge/toolLife/toolLifeCount", {**base_params, "toolLifeCount": 1}))
                life_info_tasks.append(self.machine_repo.get_data("/machine/toolArea/registerTools/toolEdge/toolLife/toolLifeAlarm", base_params))

        if not life_info_tasks:
            return "등록된 공구의 날 정보가 없습니다."

        # 3. 생성된 모든 수명 정보 태스크를 한 번에 실행
        all_results = await asyncio.gather(*life_info_tasks)

        # 4. 결과를 올바른 구조로 조합
        toolLife_info = []
        task_idx = 0  # 'results' 리스트를 순회하기 위한 인덱스 카운터
    
        for i, num_edges in enumerate(cleaned_edges_list):
            tool_num = i + 1
             # 날 개수가 유효한 정수일 때만 처리
            tool_name = tool_name_tasks[i] if not tool_name_tasks[i].get("__error__") else "error"
            for j in range(1, num_edges + 1):
                # 4개의 결과가 한 세트
                result_chunk = all_results[task_idx : task_idx + 4]

                # API 에러 처리: 5개 중 하나라도 에러면 'error'로 표기, 아니면 값 할당
                rest_life = result_chunk[0] if not result_chunk[0].get("__error__") else "error"
                max_life = result_chunk[1] if not result_chunk[1].get("__error__") else "error"
                life_count = result_chunk[2] if not result_chunk[2].get("__error__") else "error"
                life_alarm = result_chunk[3] if not result_chunk[3].get("__error__") else "error"
                
                toolLife_info.append({
                    "registerTools": tool_num,
                    "toolName": tool_name,
                    "toolEdges": j,
                    "restToolLife": rest_life,
                    "maxToolLife": max_life,
                    "toolLifeCount": life_count,
                    "toolLifeAlarm": life_alarm
                })
                task_idx += 4 # 다음 결과 세트를 위해 인덱스를 4 증가

        return toolLife_info

    async def get_categoryOfQuery(self, query: str):
        """
        - 유사도 검사를 통해 사용자의 질문이 어떤 카테고리에 속하는지 판단합니다.
        - FAISS 벡터스토어에서 가장 유사한 질문을 찾아 해당 질문의 카테고리를 반환합니다.
        Args:
            query (str): 사용자의 질문.
        Returns:
            가장 유사한 질문의 카테고리.
        
        """
        # 임베딩 객체 (검색 시에도 임베딩이 필요할 수 있습니다)
        # embeddings = HuggingFaceEmbeddings(model_name='jhgan/ko-sroberta-multitask', model_kwargs={"device": "cpu"})

        # 저장된 FAISS 벡터스토어 파일 경로
        faiss_store_path = Path(__file__).parent / "faiss_store_category.pkl"

        # pickle 파일에서 vectorstore 로드
        with open(faiss_store_path, "rb") as f:
            vectorstore = pickle.load(f)


        # 사용 예시

        # retriever.invoke 대신 vectorstore.similarity_search_with_score를 사용합니다.
        # matches_with_scores = vectorstore.similarity_search_with_score(query, k=1)
        results = vectorstore.similarity_search(query, k=1)
        return results[0].metadata['category_name']

            
    async def get_api_data(self, category: str):
        """
        - get_categoryOfQuery로부터 받은 카테고리에 해당하는 API 데이터를 반환합니다.
        - 장비 기본 정보, 채널 상태 정보, 축 상태 및 제어, 스핀들 상태 및 제어, 이송 속도 및 오버라이드, 공구 정보, NC 프로그램 실행 정보, 좌표계 및 오프셋, 알람 및 에러, PLC 및 변수, 가공 상태 및 집계, 센서 데이터 수집 중 하나를 수정하지 않고 파라미터로 받습니다.
        Args:
            category (str): get_categoryOfQuery로부터 받은 카테고리 이름.
        """
        file_path = Path(__file__).parent / "torus_manual" / "api_data_by_category.json"
        
        try:
            # 파일을 비동기적으로 열고 읽습니다.
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                file_content = await f.read()

            api_data = json.loads(file_content)
            api_info = api_data.get(category)

            if api_info:
                # 성공 시 반환 형식을 일관성 있게 유지하는 것이 좋습니다.
                return {
                    "success": True,
                    "data": api_info 
                }
            else:
                return {
                    "success": False,
                    "message": f"엔드포인트 '{category}'에 대한 정보를 찾을 수 없습니다.",
                }

        except FileNotFoundError:
            return {
                "success": False,
                "message": "API 데이터 파일을 찾을 수 없습니다. 경로를 확인하세요."
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "message": "API 데이터 JSON 파일의 형식이 잘못되었습니다."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"알 수 없는 오류가 발생했습니다: {str(e)}"
            }
            
    async def get_params_info(self, endpoint_list: List[str]):
        """
        - 여러 API 엔드포인트에 대한 필수 파라미터 정보를 한 번에 조회합니다.
        Args:
            endpoint_list: List[str] : API 엔드포인트.
            
        """
        results = {}
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, '..', 'torus_manual/uri_params.json')

        try:
            # JSON 파일을 비동기적으로 읽기
            async with aiofiles.open(json_file_path, 'r', encoding='utf-8') as f:
                file_content = await f.read()

            api_data = json.loads(file_content)
            

            for endpoint in endpoint_list:
                endpoint_info = api_data.get(endpoint)

                # 값이 존재할 경우에만 required_params를 찾습니다.
                if endpoint_info:
                    params_info = endpoint_info.get("required_params")
                else:
                    params_info = None  # 키가 없는 경우 None으로 처리
                
                results[endpoint] = params_info
                

            return results

        except FileNotFoundError:
            return {
                "__error__": True,
                "message": "URI 및 파라미터 JSON 파일을 찾을 수 없습니다. 경로를 확인하세요."
            }
        except json.JSONDecodeError:
            return {
                "__error__": True,
                "message": "URI 및 파라미터 JSON 파일의 형식이 잘못되었습니다."
            }
        except Exception as e:
            return {
            "__error__": True,
            "message": f"알 수 없는 오류가 발생했습니다: {str(e)}"
            }
            
    async def get_async_data(self, endpoint_list: List[str], params_list: List[dict]):
        """
        - 여러 API 엔드포인트에 대해 비동기적으로 데이터를 조회합니다.
        - endpoint_list와 params_list의 길이는 같아야 하며, 각 인덱스에 해당하는 엔드포인트와 파라미터로 요청이 이루어집니다.
        - 필요한 파라미터 값을 알고 있는 엔드포인트에 대해서만 호출해야 합니다.
        
        Args:
            endpoint_list (List[str]): 조회할 API 엔드포인트 리스트.
            params_list (List[dict]): 각 엔드포인트에 대한 파라미터 딕셔너리 리스트. 
        """
        
        if len(endpoint_list) != len(params_list):
            return "엔드포인트 리스트와 파라미터 리스트의 길이는 같아야 합니다."
        
        asyncio_tasks = []
        for endpoint, params in zip(endpoint_list, params_list):
            asyncio_tasks.append(self.machine_repo.get_data(endpoint, params))
        
        results = await asyncio.gather(*asyncio_tasks)
        
        return results