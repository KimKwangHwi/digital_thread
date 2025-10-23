# services/history_logger.py
from datetime import datetime
from database import get_db

class APIHistoryLogger:
    def __init__(self):
        self.db = None
        self.collection = None
    
    async def initialize(self):
        """초기화"""
        self.db = await get_db()
        self.collection = self.db.api_history
        
        # 인덱스 생성 (성능 최적화)
        await self.collection.create_index([
            ("machine_id", 1),
            ("timestamp", -1)
        ])
        print("✅ API History Logger 초기화 완료")
    
    async def log_batch(self, endpoint_list, params_list, results):
        """
        API 호출 결과 일괄 저장
        """
        if self.collection is None:
            await self.initialize()
        
        documents = []
        for endpoint, params, result in zip(endpoint_list, params_list, results):
            doc = {
                "timestamp": datetime.now(),
                "endpoint": endpoint,
                "params": params,
                "result": result,
                "machine_id": params.get("machine"),
                "is_error": self._is_error(result)
            }
            documents.append(doc)
        
        try:
            if documents:
                await self.collection.insert_many(documents)
        except Exception as e:
            print(f"⚠️ History 저장 실패: {e}")
    
    def _is_error(self, result):
        """에러 여부 확인"""
        if isinstance(result, dict) and result.get("__error__"):
            return True
        return False

# 싱글톤
history_logger = APIHistoryLogger()