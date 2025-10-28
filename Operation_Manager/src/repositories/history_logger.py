# services/history_logger.py
from datetime import datetime
from datetime import timedelta
from database import get_db
from typing import Optional, Dict, Any

class APIHistoryLogger:
    def __init__(self):
        self.db = None
        self.history_coll = None
        self.error_coll = None
    
    async def initialize(self):
        """초기화"""
        self.db = await get_db()
        self.history_coll = self.db.api_history
        self.error_coll = self.db.api_errors
        
        
        common_index = [
            ("index.endpoint", 1),
            ("index.params.machine", 1)
        ]
        
         # 일반 로그용 인덱스 (unique 조합)
        await self.history_coll.create_index(common_index)
        await self.history_coll.create_index("last_updated",  expireAfterSeconds=60 * 60 * 24 * 30)

        # 에러 로그용 인덱스 (unique 조합)
        await self.error_coll.create_index(common_index)
        await self.error_coll.create_index("last_updated",  expireAfterSeconds=60 * 60 * 24 * 30)

        print("✅ APIHistoryLogger 초기화 완료 (api_history, api_error 컬렉션 준비됨)")
        # 인덱스 생성 (성능 최적화)
        print("✅ API History Logger 초기화 완료")
    
    async def log_batch(self, endpoint_list, params_list, results):
        """
        API 호출 결과 일괄 저장
        에러 여부에 따라 서로 다른 컬렉션에 저장.
        """
        if self.history_coll is None or self.error_coll is None:
            await self.initialize()

        for endpoint, params, result in zip(endpoint_list, params_list, results):
            is_error = self._is_error(result)
            timestamp = datetime.now()

            query = {
                "index.endpoint": endpoint,
                "index.params": params
            }

            # 저장 항목 구분
            if is_error:
                log_item = {
                    "timestamp": timestamp,
                    "error_status": result.get("__error__"),
                    "raw_result": result
                }
                field = "error"
                target_coll = self.error_coll
            else:
                log_item = {
                    "timestamp": timestamp,
                    "result": result
                }
                field = "answer"
                target_coll = self.history_coll

            # 문서 upsert
            try:
                await target_coll.update_one(
                    query,
                    {
                        "$push": {field: log_item},
                        "$set": {"last_updated": timestamp},
                        "$setOnInsert": {"index": {"endpoint": endpoint, "params": params}}
                    },
                    upsert=True
                )
            except Exception as e:
                print(f"⚠️ 로그 저장 실패 ({endpoint}): {e}")
        
        
    
    def _is_error(self, result):
        """에러 여부 확인"""
        if isinstance(result, dict) and result.get("__error__"):
            return True
        return False

    async def find_logs(self, endpoint: str, params: dict, limit: int = 10, is_error: bool = False) -> Optional[Dict[str, Any]]:
        """
        특정 endpoint+params 문서에서 최근 N개 로그 조회.
        반환:
            - 문서가 존재하면 해당 문서(필요 필드만 포함)
            - 문서가 없거나 오류가 발생하면 None을 반환
            - is_error=True → 에러 컬렉션에서 조회
            - is_error=False → 정상 로그 컬렉션에서 조회
        """
        if self.history_coll is None or self.error_coll is None:
            await self.initialize()

        coll = self.error_coll if is_error else self.history_coll
        field = "error" if is_error else "answer"

        try:
            # 문서가 없을 수 있으므로 find_one 결과가 None일 수 있음
            doc = await coll.find_one(
                {"index.endpoint": endpoint, "index.params": params},
                {field: {"$slice": -limit}, "index": 1, "last_updated": 1}
            )
            # doc이 None이면 호출자(서비스)에 None을 반환
            return doc
        except Exception as e:
            # DB 접근 오류 등 예외 발생 시 로그 출력 후 None 반환
            # 실제 서비스에서는 로거를 써서 에러를 남기는 것이 좋음
            print(f"⚠️ find_logs DB error for {endpoint} {params}: {e}")
            return None
        
    
    
    async def find_logs_time(
        self,
        endpoint: str,
        params: dict,
        limit: int = 10,
        is_error: bool = False,
        start_time: datetime = None, # 시작 시간 파라미터 추가
        end_time: datetime = None    # 종료 시간 파라미터 추가
    ):
        """
        특정 endpoint+params 문서에서 start_time부터 end_time 사이에 발생한 N개 또는 특정 기간 내의 로그 조회.
        - is_error=True → 에러 컬렉션에서 조회
        - is_error=False → 정상 로그 컬렉션에서 조회
        """
        try:
            if self.history_coll is None or self.error_coll is None:
                await self.initialize()

            coll = self.error_coll if is_error else self.history_coll
            field = "error" if is_error else "answer"

            # 기본 필터 조건
            filter_query = {"index.endpoint": endpoint, "index.params": params}

        # 시간 범위 조건 추가
            time_query = {}
            if start_time:
                time_query["$gte"] = start_time
            if end_time:
                time_query["$lte"] = end_time

            if time_query:
                # MongoDB는 배열 내 객체의 필드를 쿼리할 때 "elemMatch"를 사용합니다.
                # "answer" 또는 "error" 배열의 각 요소가 "timestamp" 필드를 가지고 있다고 가정합니다.
                filter_query[field] = {"$elemMatch": {"timestamp": time_query}}

            # 프로젝션 설정: 시간 조건이 없으면 기존처럼 slice, 있으면 전체 필드
            projection = {field: {"$slice": -limit}} if not time_query else None

            # find_one 대신 find를 사용하여 여러 문서를 가져올 수 있도록 변경
            # 여기서는 하나의 문서 내에서 필터링하는 로직이므로 aggregate를 사용하는 것이 더 적합합니다.
        
            pipeline = [
                {'$match': {"index.endpoint": endpoint, "index.params": params}},
                {'$unwind': f'${field}'},
            ]

        # 시간 필터링 추가
            if time_query:
                pipeline.append({'$match': {f'{field}.timestamp': time_query}})

            # 최신순으로 정렬
            pipeline.append({'$sort': {f'{field}.timestamp': -1}})
        
            # 개수 제한
            pipeline.append({'$limit': limit})
        
            # 원래 문서 형태로 다시 그룹화 (선택적)
            pipeline.append({
                '$group': {
                    '_id': '$_id',
                    'index': {'$first': '$index'},
                    f'{field}': {'$push': f'${field}'}
                }
            })

            cursor = coll.aggregate(pipeline)
            result_docs = await cursor.to_list(length=None)

            if not result_docs:
                print(f"조건에 맞는 로그를 찾을 수 없습니다: {filter_query}")
                return None

            # 일반적으로 하나의 문서가 반환될 것으로 예상
            return result_docs if result_docs else None

        except Exception as e:
            print(f"로그 조회 중 예상치 못한 오류가 발생했습니다: {e}", exc_info=True)
            return {"error": "An unexpected error occurred."}
        
        
    # async def delete_all_logs(self):
    #     """모든 로그 삭제 (테스트용)"""
    #     if self.history_coll is None or self.error_coll is None:
    #         await self.initialize()
    #     await self.history_coll.delete_many({})
    #     await self.error_coll.delete_many({})
    #     print("✅ 모든 API 로그 삭제 완료")
        
    # async def delete_some_logs(self, days: int):
    #     """특정 일수 이전 로그 삭제 (테스트용)"""
    #     if self.history_coll is None or self.error_coll is None:
    #         await self.initialize()
    #     cutoff_date = datetime.now() - timedelta(days=days)
    #     history_result = await self.history_coll.delete_many({"last_updated": {"$lt": cutoff_date}})
    #     error_result = await self.error_coll.delete_many({"last_updated": {"$lt": cutoff_date}})
    #     print(f"✅ {days}일 이전의 API 로그 삭제 완료: history({history_result.deleted_count}), errors({error_result.deleted_count})")
# 싱글톤
history_logger = APIHistoryLogger()