---
name: torus-api-handler
description: TORUS API를 사용한 CNC 장비 데이터 조회. 공통 워크플로우 및 공구 관리(tool, 수명, life, 날, edge, T코드, 매거진, 오프셋), 축/스핀들 상태(axis, spindle, 부하, load, 위치, position, 이송, feed, RPM), 알람 정보(alarm, 에러, error, 경고, warning) 조회 시 사용. 장비 식별, 파라미터 준비, 캐싱, 비동기 데이터 조회, 시간 변환, 응답 포맷팅 제공.
---


# Tool Core workflow

# TORUS API Core Workflow

모든 TORUS API 데이터 조회에 공통으로 적용되는 필수 워크플로우와 규칙을 정의합니다.

## 전제 조건

이 Core Skill은 모든 카테고리별 TORUS Skill과 함께 사용됩니다. 카테고리별 Skill은 구체적인 엔드포인트와 도메인 지식을 제공하며, 이 Core Skill은 처리 방법을 제공합니다.

## 필수 처리 순서

**모든 TORUS API 질의는 반드시 다음 순서를 따라야 합니다:**

```
1. 장비 식별 → get_machine_list()
2. 질문 분석 → 카테고리별 Skill 참조하여 엔드포인트 식별
3. 파라미터 확인 → get_params_info(endpoint_list)
4. 캐시 확인 → get_cache_before_async_data(endpoint_list, params_list)
5. 데이터 조회 → get_async_data(endpoint_list, params_list)
6. 응답 포맷팅 → 결과를 명확하게 제시
```

**⚠️ 이 순서를 절대 건너뛰지 마세요!**

## 1단계: 장비 식별

질의에 장비가 언급되면 항상 먼저 `get_machine_list()`를 호출합니다.

### 장비명 → machine_id 매핑

```python
장비 제조사별 cncVendor 코드:
- "지멘스" / "SIEMENS" → cncVendor=2
- "화낙" / "FANUC" → cncVendor=1
- "미쓰비시" / "MITSUBISHI" → cncVendor=4
- "KCNC" → cncVendor=5
- "CSCAM" → cncVendor=3
```

`get_machine_list()` 결과에서 해당 장비의 `machine_id`를 추출하여 모든 후속 API 호출에 사용합니다.

### 복수 장비 처리

"모든 장비" 또는 "각 장비" 언급 시:
1. `get_machine_list()`로 전체 장비 목록 획득
2. 각 장비에 대해 개별적으로 데이터 조회
3. 장비별로 그룹화하여 결과 제시

## 2단계: 질문 분석

사용자 질문에서 키워드를 추출하여 해당 카테고리 Skill을 참조합니다.

### 카테고리 트리거 키워드

```
공구 관련 → tool-management Skill
- "공구", "tool", "T코드", "수명", "날", "edge"

축/스핀들 → axis-spindle-status Skill
- "축", "axis", "스핀들", "spindle", "부하", "위치"

알람 → alarm-info Skill
- "알람", "alarm", "에러", "경고"

프로그램 → program-status Skill
- "프로그램", "program", "NC", "실행", "블록"

가공 진척 → work-progress Skill
- "가공", "작업", "진척", "수량", "시간"

채널 상태 → channel-status Skill
- "채널", "channel", "계통"
```

해당 카테고리 Skill을 읽고 구체적인 엔드포인트를 식별합니다.

## 3단계: 파라미터 확인

**⚠️ 절대 건너뛰지 마세요!**

`get_async_data()`를 호출하기 전에 반드시:

```python
get_params_info(endpoint_list)
```

이 도구는 각 엔드포인트에 필요한 파라미터 정보를 반환합니다. 이 정보를 바탕으로 `params_list`를 구성하세요.

## 4단계: 캐시 확인

중복 API 호출을 방지하기 위해 캐시를 먼저 확인:

```python
get_cache_before_async_data(endpoint_list, params_list)
```

- **캐시 히트**: 반환된 데이터를 직접 사용
- **캐시 미스**: 5단계로 진행하여 데이터 조회

## 5단계: 데이터 조회

캐시되지 않은 엔드포인트에 대해서만:

```python
get_async_data(endpoint_list, params_list)
```

**중요:**
- `endpoint_list`와 `params_list`는 같은 길이
- 인덱스가 서로 대응되어야 함

## 6단계: 응답 포맷팅

데이터 양에 따라 적절한 형식 선택:

### 단일/소량 값 (1-3개)
자연스러운 문장 형식
```
지멘스 장비의 CNC 모델은 SINUMERIK 840D입니다.
```

### 중간 규모 (4-10개)
불릿 리스트 형식
```
축 부하 정보:
• X축: 45.2%
• Y축: 38.7%
• Z축: 52.1%
```

### 대량 데이터 (10개 이상)
표 형식
```
| 공구번호 | 공구명 | 최대수명 | 잔여수명 |
|---------|--------|---------|---------|
| T01     | 드릴   | 1000    | 850     |
| T02     | 엔드밀 | 500     | 120     |
```

## 공통 파라미터 규칙

### machine (항상 필수)
1단계에서 얻은 `machine_id` 사용

### channel (맥락에 따라 필수)
- **기본값**: `1`
- 사용자가 명시한 경우: 해당 번호 사용
- "모든 채널" 언급 시:
  1. `/machine/numberOfChannels` 먼저 조회
  2. `channel=1`부터 `channel=N`까지 루프

### toolArea (공구 관련 시)
- **기본값**: `1`

### axis (축 관련 시)
- 명시된 경우: 해당 번호 사용
- "X축", "Y축", "Z축" 언급 시: `axisName`으로 해당 축 찾기
- 미명시 시: **기본값 `1`**
- "모든 축" 언급 시: `numberOfAxes` 조회 후 루프

### spindle (스핀들 관련 시)
- 명시된 경우: 해당 번호 사용
- 미명시 시: **기본값 `1`**
- "모든 스핀들" 언급 시: `numberOfSpindles` 조회 후 루프

### tools (공구 번호)
- T코드 사용: "T05" → `tools=5`
- "모든 공구" 언급 시: `numberOfRegisteredTools` 조회 후 루프

### toolEdge (공구 날)
- **기본값**: `1` (첫 번째 날)
- "모든 날" 언급 시: `numberOfEdges` 조회 후 루프

## 시간 파라미터 처리

### ⚠️ 중요: 시간대 변환 필수!

**사용자는 서울 시간(UTC+9)으로 말합니다.**
**API는 UTC(+00:00)가 필요합니다.**

### 변환 방법

현재 서울 날짜: 2025-11-19 (수요일)

```python
변환 예시:

사용자: "오늘 오전 9시부터"
→ start_time = "2025-11-19T00:00:00Z"  # 서울 09:00 = UTC 00:00

사용자: "어제"
→ start_time = "2025-11-18T00:00:00Z"
→ end_time = "2025-11-18T14:59:59Z"

사용자: "11월 15일 오후 3시"
→ start_time = "2025-11-15T06:00:00Z"  # 서울 15:00 = UTC 06:00

변환 공식: UTC = 서울 시간 - 9시간
```

### 시간 범위 질의

- "오늘": `start_time=오늘 00:00 UTC`, `end_time=오늘 23:59 UTC`
- "어제": `start_time=어제 00:00 UTC`, `end_time=어제 23:59 UTC`
- "이번 주": `start_time=주 시작 00:00 UTC`, `end_time=현재 UTC`
- "최근 1시간": `start_time=현재-1시간 UTC`, `end_time=현재 UTC`

## 에러 처리

### 엔드포인트 조회 실패
- 다른 엔드포인트는 계속 처리
- 실패 항목은 "조회 실패" 또는 "N/A" 표시
- **전체 응답을 중단하지 말 것**

### 데이터 없음
- "해당 데이터가 없습니다" 명확히 표시
- 가능한 이유 설명 (예: "공구가 등록되지 않음")

### 장비를 찾을 수 없음
- `get_machine_list()`의 사용 가능한 장비 목록 제시
- 사용자에게 올바른 장비명 지정 요청

## 공통 CNC 코드 해석

### CNC 제조사 (cncVendor)
```
1: FANUC (화낙)
2: SIEMENS (지멘스)
3: CSCAM
4: MITSUBISHI (미쓰비시)
5: KCNC
```

### 운전 모드 (operateMode)
```
0: JOG (수동)
1: MDI (수동 데이터 입력)
2: MEMORY(AUTO) (자동 운전)
3: ZRN (원점 복귀)
4: MPG (핸들)
6: EDIT (편집)
7: HANDLE (핸들)
```

### NC 상태 (ncState)
```
0: Reset (리셋)
1: Stop (정지)
2: Hold (일시 정지)
3: Start (가동 중)
4: MSTR (마스터)
5: Interrupted (중단)
6: Pause (일시 중지)
```

### 비상 정지 상태 (emergencyStatus)
```
0: 정상
1: 비상 정지 중 🚨
2: 리셋
3: 대기
```

## 모범 사례

1. **순서 준수**: 6단계를 순서대로 실행
2. **캐시 활용**: 중복 호출 방지
3. **배치 요청**: 여러 엔드포인트를 한 번에 조회
4. **시간대 변환**: 항상 서울→UTC 변환 확인
5. **명확한 포맷**: 데이터 양에 맞는 형식 선택
6. **단위 해석**: 원시 코드가 아닌 의미 설명
7. **부분 성공 허용**: 일부 실패해도 나머지 결과 제공

## 제약 사항

### 답변하지 않을 질문
- CNC 장비와 무관한 질문
- TORUS API 범위 밖의 질문
- 제조/가공 데이터와 무관한 질문

관련 없는 질의는 정중하게 CNC/제조 주제로 안내하세요.

### 절대 하지 말 것
- 필수 순서 건너뛰기
- `get_params_info()` 없이 `get_async_data()` 호출
- 시간대 변환 누락
- 원시 코드만 표시 (해석 없이)
- 부분 실패 시 전체 중단

## 카테고리 Skill과의 협업

이 Core Skill은 "어떻게 처리할지"를 정의합니다.
카테고리별 Skill은 "무엇을 조회할지"를 정의합니다.

**처리 흐름:**
```
1. 사용자 질문 접수
2. Core Skill 읽기 (필수 워크플로우 파악)
3. 해당 카테고리 Skill 읽기 (구체적인 엔드포인트 파악)
4. Core Skill의 6단계 순서로 처리
5. 카테고리 Skill의 도메인 지식 활용하여 응답
```

## 참고사항

- 상세한 엔드포인트 사양은 `torus_md_res` 매뉴얼 참조
- 카테고리별 특수 처리는 해당 카테고리 Skill 참조
- 이 Core Skill은 모든 카테고리에 공통으로 적용되는 절차만 정의


# Tool Management


# 공구 관리 (Tool Management)

공구 영역, 공구 수명, 공구 상태, 현재 활성 공구 등 공구 관련 모든 정보를 조회합니다.

## 전제 조건

이 Skill을 사용하기 전에 반드시 `torus-core-workflow` Skill을 먼저 읽고 6단계 필수 처리 순서를 따르세요.

## 카테고리 개요

공구 관련 데이터는 두 가지 주요 영역으로 나뉩니다:

1. **장비 공구 영역 정보** (`/machine/toolArea/*`)
   - 공구 영역에 등록된 모든 공구 정보
   - 매거진 정보
   - T코드 기준 또는 등록순 기준 조회 가능

2. **현재 활성 공구 정보** (`/machine/channel/activeTool/*`)
   - 현재 사용 중인 공구의 실시간 정보

## 엔드포인트 구조

### 1. 장비 공구 영역 정보

```
기본 경로: /machine/toolArea/

하위 카테고리:
├── 공구 영역 기본 정보
├── 매거진 정보           /magazine/
├── T코드 기준 공구 정보   /tools/
│   ├── 공구 날 정보       /tools/toolEdge/
│   └── 공구 수명 정보     /tools/toolEdge/toolLife/
└── 등록순 기준 공구 정보  /registerTools/
    ├── 공구 날 정보       /registerTools/toolEdge/
    └── 공구 수명 정보     /registerTools/toolEdge/toolLife/
```

### 2. 현재 활성 공구 정보

```
기본 경로: /machine/channel/activeTool/

하위 카테고리:
├── 활성 공구 기본 정보
├── 공구 날 정보           /toolEdge/
└── 공구 수명 정보         /toolEdge/toolLife/
```

## 상세 엔드포인트 및 파라미터

### 공구 영역 기본 정보

**필수 파라미터**: `machine`, `toolArea`

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `toolAreaEnabled` | 공구 영역 사용 가능 여부 | BOOLEAN |
| `numberOfMagazines` | 사용 가능한 매거진 개수 | INTEGER |
| `numberOfRegisteredTools` | 공구 영역에 등록된 총 공구 개수 | INTEGER |
| `numberOfLoadedTools` | 매거진에 탑재된 총 공구 개수 | INTEGER |
| `numberOfToolGroups` | 등록된 공구 그룹 개수 | INTEGER |
| `numberOfToolOffsets` | 등록된 공구 오프셋 개수 | INTEGER |

**예시:**
```python
endpoint = "/machine/toolArea/numberOfRegisteredTools"
params = {"machine": 1, "toolArea": 1}
```

### 매거진 정보

**필수 파라미터**: `machine`, `toolArea`, `magazine`

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `magazine/magazineEnabled` | 매거진 사용 가능 여부 | BOOLEAN |
| `magazine/magazineName` | 매거진 이름 (SIEMENS 전용) | STRING |
| `magazine/numberOfRealLocations` | 매거진의 물리적 포트 개수 | INTEGER |
| `magazine/magazinePhysicalNumber` | 매거진의 물리적 번호 | INTEGER |
| `magazine/numberOfLoadedTools` | 해당 매거진에 탑재된 공구 개수 | INTEGER |

### 공구 상세 정보 (tools / registerTools 공통)

**필수 파라미터**: 
- T코드 기준: `machine`, `toolArea`, `tools`
- 등록순 기준: `machine`, `toolArea`, `registerTools`

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `locationNumber` | 매거진 탑재 위치 번호 | INTEGER |
| `toolName` | 공구 이름 | STRING |
| `toolNumber` | 공구 식별 번호 (T코드) | INTEGER |
| `numberOfEdges` | 공구 날 총 개수 | INTEGER |
| `toolEnabled` | 공구 영역 등록 및 매거진 탑재 여부<br>0: 미등록/미탑재<br>1: 등록/미탑재<br>2: 등록/탑재 | INTEGER |
| `magazineNumber` | 탑재된 매거진 번호 | INTEGER |
| `sisterToolNumber` | 대체 공구 번호 | INTEGER |
| `toolLifeUnit` | 공구 수명 측정 단위 (하단 표 참조) | INTEGER |
| `toolGroupNumber` | 공구 그룹 번호 리스트 | LIST[INTEGER] |
| `toolUseOrderNumber` | 그룹 내 사용 순서 (FANUC) | INTEGER |
| `toolStatus` | 공구 사용 상태 (하단 표 참조) | INTEGER |

### 공구 날(Edge) 정보

**필수 파라미터**: 위 파라미터 + `toolEdge`, 각 항목별 파라미터

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `toolEdge/edgeNumber` | 공구 날 식별 번호 | INTEGER |
| `toolEdge/toolType` | 공구 유형 (하단 표 참조) | INTEGER |
| `toolEdge/lengthOffsetNumber` | 길이 보정 식별 번호 | INTEGER |
| `toolEdge/geoLengthOffset` | 길이 X 보정값 | REAL |
| `toolEdge/wearLengthOffset` | 길이 X 마모 보정값 | REAL |
| `toolEdge/geoLengthOffsetZ` | 길이 Z 보정값 | REAL |
| `toolEdge/wearLengthOffsetZ` | 길이 Z 마모 보정값 | REAL |
| `toolEdge/geoLengthOffsetY` | 길이 Y 보정값 | REAL |
| `toolEdge/wearLengthOffsetY` | 길이 Y 마모 보정값 | REAL |
| `toolEdge/radiusOffsetNumber` | 반경 보정 식별 번호 | INTEGER |
| `toolEdge/geoRadiusOffset` | 반경 보정값 | REAL |
| `toolEdge/wearRadiusOffset` | 반경 마모 보정값 | REAL |
| `toolEdge/edgeEnabled` | 공구 날 사용 가능 여부 | BOOLEAN |
| `toolEdge/tipAngle` | 팁 각도 | REAL |
| `toolEdge/holderAngle` | 홀더 각도 | REAL |
| `toolEdge/insertAngle` | 인서트 각도 | REAL |
| `toolEdge/numberOfTeeth` | 공구 날 개수 (SIEMENS) | INTEGER |

### 공구 수명 정보

**필수 파라미터**: 위 파라미터 + 수명 항목별 파라미터

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `toolLife/maxToolLife` | 최대 공구 수명 | REAL |
| `toolLife/restToolLife` | 잔여 공구 수명 | REAL |
| `toolLife/toolLifeCount` | 현재 공구 사용량 | REAL |
| `toolLife/toolLifeAlarm` | 수명 경고 설정값 (SIEMENS) | REAL |

**예시:**
```python
# T코드 5번 공구의 1번 날 최대 수명
endpoint = "/machine/toolArea/tools/toolEdge/toolLife/maxToolLife"
params = {
    "machine": 1, 
    "toolArea": 1, 
    "tools": 5,
    "toolEdge": 1,
    "maxToolLife": 1
}

# 등록순 3번 공구의 1번 날 잔여 수명
endpoint = "/machine/toolArea/registerTools/toolEdge/toolLife/restToolLife"
params = {
    "machine": 1,
    "toolArea": 1,
    "registerTools": 3,
    "toolEdge": 1,
    "restToolLife": 1
}
```

### 현재 활성 공구 정보

**필수 파라미터**: `machine`, `channel`

현재 사용 중인 공구의 정보를 실시간으로 조회합니다.
엔드포인트는 위의 공구 상세 정보와 동일하되, 경로만 다릅니다:
- `/machine/channel/activeTool/toolNumber`
- `/machine/channel/activeTool/toolEdge/geoLengthOffset`
- `/machine/channel/activeTool/toolEdge/toolLife/restToolLife`

## 코드 해석 테이블

### 공구 수명 단위 (toolLifeUnit)

```
0: 단위 없음
1: 시간(분)
2: 횟수
4: 마모량
5: 횟수(장착)
6: 횟수(사용)
8: 오프셋
```

### 공구 상태 (toolStatus)

```
0: 미등록 (Not enabled)
1: 활성 공구 (Active tool) - 현재 사용 중
2: 사용 가능 (Enabled)
4: 비활성화 (Disabled)
8: 측정됨 (Measured)
9: 미사용 공구
10: 정상 수명 공구
11: 데이터 사용 가능 (using)
12: 등록됨 (available)
13: 수명 만료 🔴
14: 건너뜀 (skipped)
16: 사전 경고 도달 ⚠️
32: 교체 중 (Tool being changed)
128: 사용됨 (Tool was in use)
```

### 공구 유형 (toolType) - 주요 항목

```
10: 범용 공구
20: 드릴 (Drill)
22: 평 엔드밀 (Flat end mill)
23: 볼 엔드밀 (Ball end mill)
24: 탭 (Tap)
25: 리머 (Reamer)
26: 보링 툴 (Boring tool)
27: 페이스 밀 (Face mill)
50: 라운드 엔드밀 (Radius end mill)
110: 볼 노즈 엔드밀
120: 엔드밀
200: 트위스트 드릴
240: 탭
250: 리머
540: 나사 절삭 공구
710: 3D 프로브
```

전체 목록은 `torus_md_res` 참조

## 일반적인 질의 패턴

### 패턴 1: 모든 공구의 수명 정보

```
사용자: "지멘스에 등록된 공구들의 최대 수명과 수명 단위를 알려줘"

처리:
1. get_machine_list() → machine_id
2. /machine/toolArea/numberOfRegisteredTools 조회 → N개
3. tools=1~N에 대해:
   - /machine/toolArea/tools/toolName
   - /machine/toolArea/tools/toolLifeUnit
   - /machine/toolArea/tools/toolEdge/toolLife/maxToolLife
   - /machine/toolArea/tools/toolEdge/toolLife/restToolLife
4. 표 형식으로 출력:
   | 공구번호 | 공구명 | 최대수명 | 잔여수명 | 수명단위 | 상태 |
```

### 패턴 2: 특정 공구의 상세 정보

```
사용자: "T05 공구의 오프셋 값을 알려줘"

처리:
1. get_machine_list() → machine_id
2. tools=5로 조회:
   - /machine/toolArea/tools/toolEdge/geoLengthOffset
   - /machine/toolArea/tools/toolEdge/geoLengthOffsetZ
   - /machine/toolArea/tools/toolEdge/geoRadiusOffset
3. 오프셋 정보 출력
```

### 패턴 3: 수명 경고가 필요한 공구 찾기

```
사용자: "교체가 필요한 공구를 찾아줘"

처리:
1. 모든 공구의 수명 정보 조회
2. restToolLife < maxToolLife * 0.1 인 공구 필터링
3. 경고 수준별로 분류:
   - 🔴 즉시 교체: restToolLife = 0 또는 toolStatus = 13
   - ⚠️ 교체 임박: restToolLife < maxToolLife * 0.1
4. 우선순위 순으로 표 출력
```

### 패턴 4: 현재 사용 중인 공구 정보

```
사용자: "지금 사용 중인 공구가 뭐야?"

처리:
1. get_machine_list() → machine_id
2. /machine/channel/activeTool/ 엔드포인트 조회:
   - toolNumber (T코드)
   - toolName
   - toolEdge/toolLife/restToolLife
   - toolEdge/toolLife/maxToolLife
3. 현재 공구 정보와 수명 상태 출력
```

### 패턴 5: 매거진 상태 조회

```
사용자: "매거진에 탑재된 공구 개수를 알려줘"

처리:
1. get_machine_list() → machine_id
2. /machine/toolArea/numberOfMagazines 조회 → M개
3. magazine=1~M에 대해:
   - magazineName
   - numberOfLoadedTools
   - numberOfRealLocations
4. 매거진별 탑재 현황 출력
```

## 수명 관리 가이드라인

### 수명 경고 기준

```python
위험 수준 판단:
- restToolLife = 0 → 🔴 즉시 교체 필요
- toolStatus = 13 → 🔴 수명 만료
- restToolLife < maxToolLife * 0.1 → ⚠️ 교체 임박 (10% 미만)
- restToolLife < maxToolLife * 0.2 → ⚠️ 주의 필요 (20% 미만)
```

### 수명 백분율 계산

```python
잔여 수명(%) = (restToolLife / maxToolLife) * 100

예시:
maxToolLife = 1000, restToolLife = 850
→ 85% 수명 남음 (정상)

maxToolLife = 1000, restToolLife = 50
→ 5% 수명 남음 (⚠️ 교체 임박)
```

## tools vs registerTools 선택 가이드

### tools (T코드 기준)
- T코드 번호로 공구 지정: "T05 공구"
- 특정 공구 빠른 조회
- 사용자가 T코드를 알고 있을 때

### registerTools (등록순 기준)
- 등록된 순서대로 조회
- 전체 공구 목록을 순회할 때
- T코드를 모를 때

**대부분의 경우 tools를 사용하는 것이 직관적입니다.**

## 특수 처리 사항

### 여러 날(edge)이 있는 공구

공구에 여러 날이 있을 수 있습니다:
1. `numberOfEdges`로 날 개수 확인
2. 사용자가 특정 날을 지정하지 않으면 `toolEdge=1` (첫 번째 날) 사용
3. "모든 날" 요청 시 루프 처리

### FANUC vs SIEMENS 차이

- **FANUC**: 공구 영역과 계통이 동일 (toolArea = channel)
- **SIEMENS**: 공구 영역과 계통이 1:다 관계

대부분의 경우 `toolArea=1` 사용하면 됩니다.

## 에러 처리

### 공구가 등록되지 않음
```
numberOfRegisteredTools = 0
→ "등록된 공구가 없습니다"
```

### 특정 T코드 공구 없음
```
tools=5 조회 실패
→ "T05 공구가 등록되지 않았습니다"
```

### 수명 정보 없음
```
toolLifeUnit = 0
→ "공구 수명 단위가 설정되지 않음"
```

## 참고사항

- 상세 파라미터 정보는 `get_params_info()` 사용
- 공구 유형 전체 목록은 `torus_md_res` 참조
- 처리 순서는 `torus-core-workflow` 참조


# Axis & Spindle Status


# 축/스핀들 상태 (Axis & Spindle Status)

CNC 장비의 축과 스핀들 상태 정보를 조회합니다.

## 전제 조건

이 Skill을 사용하기 전에 반드시 `torus-core-workflow` Skill을 먼저 읽고 6단계 필수 처리 순서를 따르세요.

## 카테고리 개요

축과 스핀들 데이터는 다음으로 구성됩니다:

1. **축 별 상태 정보** (`/machine/channel/axis/*`)
   - 위치 정보 (기계/공작물/상대 좌표)
   - 부하, 이송 속도, 전류, 온도
   - 전력 소비 정보

2. **스핀들 별 상태 정보** (`/machine/channel/spindle/*`)
   - 회전 속도 (RPM)
   - 부하, 전류, 온도
   - 전력 소비 정보

3. **축 이송 정보** (`/machine/channel/feed/*`)
   - 이송 속도 (지령/실제)
   - 오버라이드 비율

## 엔드포인트 구조

### 1. 축 상태 정보

```
기본 경로: /machine/channel/axis/

하위 카테고리:
├── 축 일반 정보
└── 축 전력 정보           /axisPower/
```

### 2. 스핀들 상태 정보

```
기본 경로: /machine/channel/spindle/

하위 카테고리:
├── 스핀들 일반 정보
├── RPM 정보               /rpm/
└── 스핀들 전력 정보       /spindlePower/
```

### 3. 축 이송 정보

```
기본 경로: /machine/channel/feed/

하위 카테고리:
├── 오버라이드 정보
└── 이송 속도 정보         /feedRate/
```

## 상세 엔드포인트 및 파라미터

### 축 일반 정보

**필수 파라미터**: `machine`, `channel`, `axis`

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `machinePosition` | 기계 좌표계 기준 현재 위치 | REAL |
| `workPosition` | 공작물 좌표계 기준 현재 위치 | REAL |
| `distanceToGo` | 지령 위치까지 남은 이동 거리 | REAL |
| `relativePosition` | 상대 좌표계 기준 현재 위치 | REAL |
| `axisName` | 절대 좌표계의 축 이름 | STRING |
| `relativeAxisName` | 상대 좌표계의 축 이름 (FANUC) | STRING |
| `axisLoad` | 축에 걸리는 부하 (%) | REAL |
| `axisFeed` | 현재 축의 이송 속도 | REAL |
| `axisLimitPlus` | '+' 방향 최대 이동 한계값 | REAL |
| `axisLimitMinus` | '-' 방향 최대 이동 한계값 | REAL |
| `workAreaLimitPlus` | 작업 금지 영역 '+' 방향 한계값 | REAL |
| `workAreaLimitMinus` | 작업 금지 영역 '-' 방향 한계값 | REAL |
| `workAreaLimitPlusEnabled` | 작업 금지 영역 '+' 활성화 여부 | BOOLEAN |
| `workAreaLimitMinusEnabled` | 작업 금지 영역 '-' 활성화 여부 | BOOLEAN |
| `axisEnabled` | 축 사용 가능 여부 | BOOLEAN |
| `interlockEnabled` | 인터락 상태 여부 | BOOLEAN |
| `constantSurfaceSpeedControlEnabled` | 주속 일정 제어(CSS) 활성화 | BOOLEAN |
| `axisCurrent` | 축 전류 정보 | REAL |
| `machineOrigin` | 기계 원점 좌표값 | REAL |
| `axisTemperature` | 축 온도 정보 | REAL |

**예시:**
```python
# X축의 부하 조회
endpoint = "/machine/channel/axis/axisLoad"
params = {"machine": 1, "channel": 1, "axis": 1}

# Z축의 기계 좌표 위치
endpoint = "/machine/channel/axis/machinePosition"
params = {"machine": 1, "channel": 1, "axis": 3}
```

### 축 전력 정보

**필수 파라미터**: `machine`, `channel`, `axis`, 각 항목별 파라미터

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `axisPower/actualPowerConsumption` | 실 소비 전력 적산값 | REAL |
| `axisPower/powerConsumption` | 소비 전력 적산값 | REAL |
| `axisPower/regeneratedPower` | 회생 전력 적산값 | REAL |

**예시:**
```python
endpoint = "/machine/channel/axis/axisPower/powerConsumption"
params = {
    "machine": 1, 
    "channel": 1, 
    "axis": 1,
    "powerConsumption": 1
}
```

### 스핀들 일반 정보

**필수 파라미터**: `machine`, `channel`, `spindle`

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `spindleLoad` | 스핀들에 걸리는 부하 (%) | REAL |
| `spindleOverride` | 스핀들 속도 오버라이드 비율 (%) | REAL |
| `spindleLimit` | 최대 회전 속도 한계값 | REAL |
| `spindleEnabled` | 스핀들 사용 가능 여부 | BOOLEAN |
| `spindleCurrent` | 스핀들 전류 정보 | REAL |
| `spindleTemperature` | 스핀들 온도 정보 | REAL |

### 스핀들 RPM 정보

**필수 파라미터**: `machine`, `channel`, `spindle`, 각 항목별 파라미터

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `rpm/commandedSpeed` | 지령된 스핀들 회전 속도 | REAL |
| `rpm/actualSpeed` | 실제 측정된 스핀들 회전 속도 | REAL |
| `rpm/speedUnit` | 속도 단위 (하단 표 참조) | INTEGER |

**예시:**
```python
# 스핀들의 실제 회전 속도
endpoint = "/machine/channel/spindle/rpm/actualSpeed"
params = {
    "machine": 1,
    "channel": 1,
    "spindle": 1,
    "actualSpeed": 1
}
```

### 스핀들 전력 정보

**필수 파라미터**: `machine`, `channel`, `spindle`, 각 항목별 파라미터

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `spindlePower/actualPowerConsumption` | 실 소비 전력 적산값 | REAL |
| `spindlePower/powerConsumption` | 소비 전력 적산값 | REAL |
| `spindlePower/regeneratedPower` | 회생 전력 적산값 | REAL |

### 축 이송 오버라이드

**필수 파라미터**: `machine`, `channel`

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `feedOverride` | 가공 이송 속도 오버라이드 비율 (%) | REAL |
| `rapidOverride` | 급속 이송 속도 오버라이드 비율 (%) | REAL |

**예시:**
```python
endpoint = "/machine/channel/feed/feedOverride"
params = {"machine": 1, "channel": 1}
```

### 축 이송 속도

**필수 파라미터**: `machine`, `channel`, 각 항목별 파라미터

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `feedRate/commandedSpeed` | 지령된 이송 속도 | REAL |
| `feedRate/actualSpeed` | 실제 측정된 이송 속도 | REAL |
| `feedRate/speedUnit` | 속도 단위 (하단 표 참조) | INTEGER |

**예시:**
```python
endpoint = "/machine/channel/feed/feedRate/actualSpeed"
params = {
    "machine": 1,
    "channel": 1,
    "actualSpeed": 1
}
```

## 코드 해석 테이블

### 속도 단위 (speedUnit)

```
0: mm/min (밀리미터/분)
1: inch/min (인치/분)
2: rpm (회전수/분)
3: mm/rev (밀리미터/회전)
4: inch/rev (인치/회전)
```

## 일반적인 질의 패턴

### 패턴 1: 모든 축의 부하 조회

```
사용자: "지멘스 장비의 각 축에 걸리는 부하를 알려줘"

처리:
1. get_machine_list() → machine_id
2. /machine/channel/axis/numberOfAxes 조회 (또는 machine 정보에서 확인) → N개
3. axis=1~N에 대해:
   - /machine/channel/axis/axisName
   - /machine/channel/axis/axisLoad
4. 불릿 리스트 또는 표로 출력:
   • X축: 45.2%
   • Y축: 38.7%
   • Z축: 52.1%
```

### 패턴 2: 특정 축의 상세 정보

```
사용자: "Z축의 현재 위치와 부하를 알려줘"

처리:
1. get_machine_list() → machine_id
2. axisName="Z"인 축 찾기 (일반적으로 axis=3)
3. 조회:
   - /machine/channel/axis/machinePosition (기계 좌표)
   - /machine/channel/axis/workPosition (공작물 좌표)
   - /machine/channel/axis/axisLoad (부하)
4. 출력:
   Z축 상태:
   • 기계 좌표: 123.45 mm
   • 공작물 좌표: 23.45 mm
   • 부하: 52.1%
```

### 패턴 3: 축 전력 소비 조회

```
사용자: "지멘스의 Z축 소비 전력 적산값을 알려줘"

처리:
1. get_machine_list() → machine_id
2. Z축(axis=3) 전력 정보 조회:
   - /machine/channel/axis/axisPower/powerConsumption
   - /machine/channel/axis/axisPower/actualPowerConsumption
   - /machine/channel/axis/axisPower/regeneratedPower
3. 출력:
   Z축 전력 정보:
   • 소비 전력 적산: 1234.5 kWh
   • 실 소비 전력: 1150.2 kWh
   • 회생 전력: 84.3 kWh
```

### 패턴 4: 스핀들 회전 속도 조회

```
사용자: "스핀들 RPM을 알려줘"

처리:
1. get_machine_list() → machine_id
2. 스핀들 정보 조회:
   - /machine/channel/spindle/rpm/commandedSpeed (지령 속도)
   - /machine/channel/spindle/rpm/actualSpeed (실제 속도)
   - /machine/channel/spindle/rpm/speedUnit (단위)
3. 단위 해석 후 출력:
   스핀들 회전 속도:
   • 지령: 3000 rpm
   • 실제: 2985 rpm
   • 차이: -15 rpm (-0.5%)
```

### 패턴 5: 이송 속도 및 오버라이드

```
사용자: "현재 이송 속도와 오버라이드를 알려줘"

처리:
1. get_machine_list() → machine_id
2. 이송 정보 조회:
   - /machine/channel/feed/feedRate/commandedSpeed
   - /machine/channel/feed/feedRate/actualSpeed
   - /machine/channel/feed/feedOverride
   - /machine/channel/feed/rapidOverride
3. 출력:
   이송 정보:
   • 지령 이송 속도: 1500 mm/min
   • 실제 이송 속도: 1425 mm/min
   • 가공 이송 오버라이드: 95%
   • 급속 이송 오버라이드: 100%
```

### 패턴 6: 부하가 높은 축 찾기

```
사용자: "부하가 80% 이상인 축이 있어?"

처리:
1. 모든 축의 부하 조회
2. axisLoad >= 80 인 축 필터링
3. 경고 수준별 분류:
   - 🔴 과부하 위험: axisLoad >= 90%
   - ⚠️ 주의 필요: 80% <= axisLoad < 90%
4. 해당 축 정보 출력 (없으면 "정상 범위" 메시지)
```

## 축 식별 방법

### 축 번호 vs 축 이름

일반적인 축 매핑:
```
axis=1 → X축 (axisName="X")
axis=2 → Y축 (axisName="Y")
axis=3 → Z축 (axisName="Z")
axis=4 → A축 또는 4축 (axisName="A" 또는 "4")
```

사용자가 "X축", "Y축", "Z축"으로 요청하면:
1. `axisName`으로 해당 축 찾기
2. 일반적인 매핑 사용 (X=1, Y=2, Z=3)

### 모든 축 조회

"모든 축" 또는 "각 축" 언급 시:
1. `numberOfAxes` 조회 (machine 정보 또는 별도 엔드포인트)
2. `axis=1`부터 `axis=N`까지 루프
3. 각 축의 `axisName`과 함께 데이터 제시

## 부하 및 상태 해석

### 축 부하 (axisLoad)

```
정상 범위: 0~70%
주의 필요: 70~85%
경고: 85~90% ⚠️
위험: 90% 이상 🔴
```

### 스핀들 부하 (spindleLoad)

```
정상 범위: 0~75%
주의 필요: 75~85%
경고: 85~90% ⚠️
위험: 90% 이상 🔴
```

### 지령 vs 실제 속도 차이

```python
차이율 = ((actualSpeed - commandedSpeed) / commandedSpeed) * 100

정상 범위: ±2% 이내
주의: ±2~5%
경고: ±5% 이상 ⚠️
```

## 특수 처리 사항

### CSS (주속 일정 제어)

`constantSurfaceSpeedControlEnabled=true`인 경우:
- 선삭 작업에서 주로 사용
- 스핀들 속도가 자동으로 조정됨
- 이 정보를 사용자에게 알려줄 수 있음

### 인터락 상태

`interlockEnabled=true`인 경우:
- 축이 잠김 상태
- 안전상의 이유로 이동 불가
- 🔒 인터락 활성화 표시

### 작업 금지 영역

`workAreaLimitPlusEnabled` 또는 `workAreaLimitMinusEnabled`가 true인 경우:
- 해당 방향으로 제한된 이동 범위
- 안전 영역 설정됨을 표시

## 전력 데이터 해석

### 회생 전력 (regeneratedPower)

```
회생 효율 = (regeneratedPower / powerConsumption) * 100

예시:
소비 전력: 1000 kWh
회생 전력: 150 kWh
→ 15% 회생 효율
```

### 실 소비 전력

```
실 소비 전력 = 소비 전력 - 회생 전력
```

## 에러 처리

### 축이 비활성화됨
```
axisEnabled = false
→ "해당 축은 현재 비활성화 상태입니다"
```

### 스핀들이 비활성화됨
```
spindleEnabled = false
→ "해당 스핀들은 현재 비활성화 상태입니다"
```

### 데이터 조회 실패
- 부분 데이터라도 제공
- 실패한 항목은 "N/A" 표시

## 참고사항

- 상세 파라미터 정보는 `get_params_info()` 사용
- 축/스핀들 개수는 machine 정보에서 확인 가능
- 처리 순서는 `torus-core-workflow` 참조


# Alarm Info



# 알람 정보 (Alarm Information)

CNC 장비에서 발생한 알람 및 에러 정보를 조회합니다.

## 전제 조건

이 Skill을 사용하기 전에 반드시 `torus-core-workflow` Skill을 먼저 읽고 6단계 필수 처리 순서를 따르세요.

## 카테고리 개요

알람 데이터는 채널(계통)별로 관리되며, 다음 정보를 포함합니다:

1. **채널 알람 상태** - 알람 발생 여부 및 개수
2. **개별 알람 상세** - 각 알람의 내용, 카테고리, 번호, 발생 시각

## 엔드포인트 구조

```
기본 경로: /machine/channel/alarm/

조회 가능한 정보:
├── alarmText          - 알람 상세 내용
├── alarmCategory      - 알람 유형/카테고리
├── alarmNumber        - 알람 번호
└── raisedTimeStamp    - 알람 발생 시각
```

## 상세 엔드포인트 및 파라미터

### 채널 알람 상태

**필수 파라미터**: `machine`, `channel`

채널 상태 정보에서 알람 관련 항목:

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `/machine/channel/alarmStatus` | 채널의 알람 상태 (하단 표 참조) | INTEGER |
| `/machine/channel/numberOfAlarms` | 해당 채널에서 발생한 알람 총 개수 | INTEGER |

### 개별 알람 상세 정보

**필수 파라미터**: `machine`, `channel`, `alarm`

| 엔드포인트 | 설명 | 데이터 타입 |
|-----------|------|------------|
| `alarmText` | 알람 상세 내용 | STRING |
| `alarmCategory` | 알람 유형/카테고리 | STRING |
| `alarmNumber` | 알람 번호 | STRING |
| `raisedTimeStamp` | 알람 발생 시각 | STRING |

**예시:**
```python
# 첫 번째 발생 알람의 상세 내용
endpoint = "/machine/channel/alarm/alarmText"
params = {"machine": 1, "channel": 1, "alarm": 1}

# 두 번째 알람의 카테고리
endpoint = "/machine/channel/alarm/alarmCategory"
params = {"machine": 1, "channel": 1, "alarm": 2}
```

## 코드 해석 테이블

### 알람 상태 (alarmStatus)

```
0: 알람 없음 (No alarm)
1: 알람 발생 (Alarm) 🚨
2: 정지 없는 알람 (Alarm without stop) ⚠️
3: 정지를 동반한 알람 (Alarm with stop) 🔴
4: 배터리 부족 (Battery low) 🔋
5: 팬 경고 (FAN)
6: 전원 경고 (PS warning)
7: FSSB 경고 (FSSB warning)
8: 절연 경고 (Insulate warning)
9: 엔코더 경고 (Encoder warning)
10: PMC 알람 (PMC alarm)
```

## 일반적인 질의 패턴

### 패턴 1: 장비의 알람 발생 여부 확인

```
사용자: "지멘스에 알람이 발생했어?"

처리:
1. get_machine_list() → machine_id
2. 채널 알람 상태 조회:
   - /machine/channel/alarmStatus
   - /machine/channel/numberOfAlarms
3. 상태에 따라 응답:
   - alarmStatus = 0 → "알람이 발생하지 않았습니다"
   - alarmStatus > 0 → "🚨 알람이 발생했습니다" + 상세 정보
```

### 패턴 2: 발생한 모든 알람 조회

```
사용자: "각 장비에 발생한 알람 정보를 조회해줘"

처리:
1. get_machine_list() → 모든 장비
2. 각 장비에 대해:
   - /machine/channel/numberOfAlarms 조회 → N개
   - alarm=1~N에 대해:
     * alarmText
     * alarmCategory  
     * alarmNumber
     * raisedTimeStamp
3. 장비별로 그룹화하여 표 형식 출력:
   
   [지멘스 장비]
   | 번호 | 카테고리 | 알람 내용 | 발생 시각 |
   |-----|---------|----------|----------|
   | 1   | 시스템   | 비상정지  | 14:23:15 |
   
   [화낙 장비]
   알람 없음 ✓
```

### 패턴 3: 특정 알람 상세 정보

```
사용자: "첫 번째 알람이 뭐야?"

처리:
1. get_machine_list() → machine_id
2. alarm=1 상세 정보 조회:
   - alarmText
   - alarmCategory
   - alarmNumber
   - raisedTimeStamp
3. 상세 정보 출력:
   🚨 알람 #1 상세:
   • 카테고리: 서보 시스템
   • 번호: SV0401
   • 내용: Z축 서보 오버로드
   • 발생 시각: 2025-11-19 14:23:15
```

### 패턴 4: 심각도별 알람 분류

```
사용자: "심각한 알람이 있어?"

처리:
1. alarmStatus 조회
2. 심각도 판단:
   - alarmStatus = 3 → 🔴 긴급 (정지를 동반한 알람)
   - alarmStatus = 1 → 🚨 경고 (일반 알람)
   - alarmStatus = 2 → ⚠️ 주의 (정지 없는 알람)
3. 심각도별로 분류하여 출력
```

### 패턴 5: 최근 알람 이력

```
사용자: "최근에 발생한 알람을 시간순으로 보여줘"

처리:
1. numberOfAlarms 조회 → N개
2. alarm=1~N 모두 조회
3. raisedTimeStamp 기준으로 정렬 (최신순)
4. 표 형식으로 출력:
   | 발생 시각 | 카테고리 | 알람 내용 |
   |----------|---------|----------|
   | 14:25:30 | 전원    | 전압 불안정 |
   | 14:23:15 | 서보    | Z축 오버로드 |
```

## 알람 분석 및 해석

### 심각도 수준

```
🔴 긴급 (Critical):
- alarmStatus = 3 (정지를 동반한 알람)
- 즉시 조치 필요
- 장비 가동 중단

🚨 경고 (Warning):
- alarmStatus = 1 (일반 알람)
- 빠른 시일 내 조치 필요
- 장비 가동 가능하나 주의

⚠️ 주의 (Notice):
- alarmStatus = 2 (정지 없는 알람)
- 모니터링 필요
- 정상 가동 중

🔋 유지보수:
- alarmStatus = 4~10 (시스템 경고)
- 예방 정비 필요
```

### 알람 카테고리별 분류

일반적인 알람 카테고리:
```
• 서보 시스템 (Servo)
• 스핀들 (Spindle)
• PMC (Programmable Machine Controller)
• 시스템 (System)
• 전원 (Power)
• 통신 (Communication)
• 과열 (Overheat)
• 오버로드 (Overload)
```

### 알람 번호 패턴

제조사별 알람 번호 체계:

**FANUC:**
```
000번대: 파라미터 관련
100번대: 서보 관련
200번대: PMC 관련
300번대: 스핀들 관련
400번대: 오버트래블
```

**SIEMENS:**
```
1xxxx: 일반 알람
2xxxx: 서보 알람
3xxxx: NC 알람
6xxxx: 시스템 알람
```

## 특수 처리 사항

### 복수 채널의 알람

장비에 여러 채널이 있는 경우:
1. 각 채널별로 알람 조회
2. 채널 번호와 함께 알람 표시
3. 채널별로 그룹화

```
[채널 1]
• 알람 없음 ✓

[채널 2]
• 🚨 서보 오버로드
• ⚠️ 공구 수명 경고
```

### 알람 없음 케이스

```
numberOfAlarms = 0 또는 alarmStatus = 0
→ "현재 발생한 알람이 없습니다 ✓"
→ "장비가 정상 가동 중입니다"
```

### 알람 발생 시각 포맷

`raisedTimeStamp` 형식: ISO 8601
```
예: "2025-11-19T14:23:15+09:00"

사용자에게 보여줄 때:
→ "2025-11-19 14:23:15" (간단한 형식)
→ "11월 19일 오후 2시 23분" (자연스러운 형식)
```

## 알람 대응 가이드

### 즉시 조치가 필요한 알람 (🔴)

```
alarmStatus = 3 또는 특정 카테고리:
- 비상정지
- 서보 오버로드
- 스핀들 과열
- 충돌 감지

→ "⚠️ 즉시 조치가 필요합니다"
→ 알람 내용과 함께 경고 표시
```

### 모니터링이 필요한 알람 (⚠️)

```
alarmStatus = 2 또는 시스템 경고:
- 배터리 부족
- 팬 경고
- 공구 수명 경고

→ "주의: 예방 점검이 필요합니다"
```

## 알람 통계 및 분석

### 알람 개수 분석

```python
사용자: "어느 장비에서 알람이 가장 많이 발생했어?"

처리:
1. 모든 장비의 numberOfAlarms 조회
2. 내림차순 정렬
3. 상위 장비 표시:
   
   알람 발생 현황:
   1. 지멘스 #1: 5건 🔴
   2. 화낙 #2: 2건 ⚠️
   3. 미쓰비시 #3: 0건 ✓
```

### 알람 카테고리별 집계

```python
사용자: "어떤 종류의 알람이 가장 많아?"

처리:
1. 모든 알람의 alarmCategory 수집
2. 카테고리별 빈도 계산
3. 그래프 또는 리스트로 출력:
   
   알람 유형별 분포:
   • 서보 시스템: 3건 (50%)
   • 스핀들: 2건 (33%)
   • 시스템: 1건 (17%)
```

## 로그 도구 활용

알람 이력 조회 시 `get_log_data` 도구 활용 가능:

```python
# 최근 1시간 동안의 알람 로그
get_log_data(
    endpoint="/machine/channel/alarm/alarmText",
    params={"machine": 1, "channel": 1, "alarm": 1},
    start_time="2025-11-19T13:00:00Z",
    end_time="2025-11-19T14:00:00Z",
    is_error=True
)
```

## 에러 처리

### 알람 정보 조회 실패
```
alarm=N 조회 실패
→ "N번째 알람 정보를 가져올 수 없습니다"
→ 다른 알람은 계속 조회
```

### 채널이 비활성화됨
```
channelEnabled = false
→ "해당 채널은 현재 비활성화 상태입니다"
```

## 출력 형식 가이드

### 알람이 없는 경우
```
✓ 정상 가동 중
현재 발생한 알람이 없습니다.
```

### 단일 알람
```
🚨 알람 발생

카테고리: 서보 시스템
번호: SV0401
내용: Z축 서보 오버로드
발생 시각: 2025-11-19 14:23:15
```

### 복수 알람 (표 형식)
```
🚨 총 3건의 알람 발생

| # | 카테고리 | 번호 | 내용 | 발생 시각 |
|---|---------|-----|------|----------|
| 1 | 서보 | SV0401 | Z축 오버로드 | 14:23:15 |
| 2 | 시스템 | SYS101 | 배터리 부족 | 14:20:30 |
| 3 | 스핀들 | SP201 | 과열 경고 | 14:18:45 |
```

## 참고사항

- 상세 파라미터 정보는 `get_params_info()` 사용
- 알람 이력은 `get_log_data()` 도구 활용
- 채널 상태 정보는 `channel-status` Skill 참조
- 처리 순서는 `torus-core-workflow` 참조
- 제조사별 알람 코드 체계는 장비 매뉴얼 참조
