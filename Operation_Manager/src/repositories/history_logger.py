# services/history_logger.py
from datetime import datetime
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
        
    
    
    
# 싱글톤
history_logger = APIHistoryLogger()