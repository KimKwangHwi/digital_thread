from datetime import datetime
from zoneinfo import ZoneInfo

# 한국 시간으로 현재 시각 가져오기
now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
print(now_kst)