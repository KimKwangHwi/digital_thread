[URI 생성 예시]
장비 모델명 조회
data://machine/cncModel?machine=1

첫 번째 장비의 첫 번째 채널, 두 번째 축의 부하 조회
data://machine/channel/axis/axisLoad?machine=1&channel=1&axis=2

첫 번째 장비의 첫 번째 채널, 첫 번째 스핀들의 소비 전력 조회
data://machine/channel/spindle/spindlePower/powerConsumption?machine=1&channel=1&spindle=1


### 데이터 모델 계층 구조, 각 데이터 설명, 필요 파라미터

machine/ **machine=i : i번째 장비**
    # 설명: 단위 공작기계를 식별하고 해당 장비에 대한 상태 정보를 나타냅니다. 다중 장비 연결 시 `machine` 필터는 필수입니다.
    ├── cncModel (STRING): 해당 장비에 탑재된 NC의 모델명.
    ├── numberOfChannels (INTEGER): 장비에서 사용 가능한 채널(계통)의 개수.
    ├── cncVendor (INTEGER): NC 제조사 코드 (1: FANUC, 2: SIEMENS, 3: CSCAM, 4: MITSUBISHI, 5: KCNC).
    ├── ncLinkState (BOOLEAN): NC와의 통신 가능 여부.
    ├── currentAccessLevel (INTEGER): 프로그램/디렉토리 접근에 대한 사용 권한 수준 (SIEMENS 전용, 1:제조자, 2:서비스, 3:사용자, 4: 프로그래머(키 스위치 3), 5: 공인 전문가(키 스위치2), 6:숙련된 전문가(키 스위치1) 7:준 숙련 전문가(키 스위치 0))
    ├── basicLengthUnit (INTEGER): 장비가 사용하는 기본 길이 단위 (0: Metric, 1: Inches 등).
    ├── machinePowerOnTime (REAL): 장비의 전원이 켜진 시간 (단위: 분).
    ├── currentCncTime (STRING): 장비에 설정된 현재 시각 (형식: yyyy-MM-ddTHH:mm:ss).
    ├── machineType (INTEGER): 장비의 타입 (0: 알 수 없음, 1: Milling, 2: Lathe 등).
    ├── ncMemory/
    │   # 설명: NC 프로그램 저장 메모리 용량에 관한 정보를 포함합니다.
    │   ├── totalCapacity (REAL): NC 메모리의 전체 용량 (단위: byte).
    │   ├── usedCapacity (REAL): 사용 중인 NC 메모리 용량 (단위: byte).
    │   ├── freeCapacity (REAL): NC 메모리의 남은 용량 (단위: byte).
    │   └── rootPath (STRING): NC 메모리의 기본(루트) 경로.
    ├── channel/ **channel=j : j번째 채널**
    │   # 설명: 채널 별 상태 정보로, 축, 스핀들, 프로그램 등 대부분의 중요 데이터를 포함하는 리스트 구조입니다.
    │   ├── channelEnabled (BOOLEAN): 해당 채널의 활성화 여부.
    │   ├── toolAreaNumber (INTEGER): 해당 채널에서 사용 가능한 공구 영역의 식별 번호. 단계통 장비의 경우 디폴트로 1. FANUC에서는 공구 영역과 계통이 동일하기 때문에 channel과 toolArea가 같은 개념으로 사용. 
                  SIEMENS의 공구 영역의 개수는 계통 수와 동등하며, 공구 영역과 계통 간 1:다 관계가 성립. 하나의 공구 영역은 여러 개의 계통에 의해 참조될 수 있지만, 하나의 계통이 여러 개의 공구 영역을 참조하는 것은 불가능
    │   ├── numberOfAxes (INTEGER): 해당 채널에서 사용 가능한 축의 개수.
    │   ├── numberOfSpindles (INTEGER): 해당 채널에서 사용 가능한 스핀들의 개수.
    │   ├── alarmStatus (INTEGER): 채널의 알람 상태 (0: No alarm, 1: Alarm 등).
    │   ├── numberOfAlarms (INTEGER): 해당 채널에서 발생한 알람의 총 개수.
    │   ├── operateMode (INTEGER): 공작기계의 운전 모드 (0: JOG, 1: MDI, 2: MEMORY 등).
    │   ├── numberOfWorkOffsets (INTEGER): 사용 가능한 공작물 좌표계의 개수.
    │   ├── ncState (INTEGER): CNC의 작동 상태 (0: Reset, 1: Stop, 2: Hold, 3: Start 등).
    │   ├── motionStatus (INTEGER): 장비의 현재 모션 상태 (1: Motion, 2: Dwell 등).
    │   ├── emergencyStatus (INTEGER): 비상 정지(Emergency) 상태 여부 (0: Not emergency, 1: Emergency).
    │   ├── axis/ **axis=k : k번째 축**
    │   │   # 설명: 축 별 상태 정보로, 위치, 부하 등을 포함하는 리스트 구조입니다.
    │   │   ├── machinePosition (REAL): 기계 좌표계 기준 현재 위치.
    │   │   ├── workPosition (REAL): 공작물 좌표계 기준 현재 위치.
    │   │   ├── distanceToGo (REAL): 지령 위치까지 남은 이동 거리.
    │   │   ├── relativePosition (REAL): 상대 좌표계 기준 현재 위치.
    │   │   ├── axisName (STRING): 절대 좌표계의 축 이름.
    │   │   ├── relativeAxisName (STRING): 상대 좌표계의 축 이름 (FANUC 전용).
    │   │   ├── axisLoad (REAL): 축에 걸리는 부하.
    │   │   ├── axisFeed (REAL): 현재 축의 이송 속도.
    │   │   ├── axisLimitPlus (REAL): '+' 방향 최대 이동 한계값.
    │   │   ├── axisLimitMinus (REAL): '-' 방향 최대 이동 한계값.
    │   │   ├── workAreaLimitPlus (REAL): 작업 금지 영역 '+' 방향 한계값.
    │   │   ├── workAreaLimitMinus (REAL): 작업 금지 영역 '-' 방향 한계값.
    │   │   ├── workAreaLimitPlusEnabled (BOOLEAN): 작업 금지 영역 '+' 방향 활성화 여부.
    │   │   ├── workAreaLimitMinusEnabled (BOOLEAN): 작업 금지 영역 '-' 방향 활성화 여부.
    │   │   ├── axisEnabled (BOOLEAN): 해당 축의 사용 가능 여부.
    │   │   ├── interlockEnabled (BOOLEAN): 해당 축의 인터락 상태 여부.
    │   │   ├── constantSurfaceSpeedControlEnabled (BOOLEAN): 주속 일정 제어(CSS) 활성화 여부.
    │   │   ├── axisCurrent (REAL): 해당 축의 전류 정보.
    │   │   ├── machineOrigin (REAL): 기계 원점 좌표값.
    │   │   ├── axisTemperature (REAL): 해당 축의 온도 정보.
    │   │   └── axisPower/
    │   │       # 설명: 축의 전력 소비량 정보.
    │   │       ├── actualPowerConsumption (REAL): 실 소비 전력의 적산값 (소비전력 - 회생전력).
    │   │       ├── powerConsumption (REAL): 소비 전력의 적산값.
    │   │       └── regeneratedPower (REAL): 회생 전력의 적산값.
    │   ├── spindle/ **spindle=k : k번째 스핀들**
    │   │   # 설명: 스핀들 별 상태 정보로, 속도, 부하 등을 포함하는 리스트 구조입니다.
    │   │   ├── spindleLoad (REAL): 스핀들에 걸리는 부하.
    │   │   ├── spindleOverride (REAL): 스핀들 속도 오버라이드 비율.
    │   │   ├── spindleLimit (REAL): 최대 회전 속도 한계값.
    │   │   ├── spindleEnabled (BOOLEAN): 해당 스핀들의 사용 가능 여부.
    │   │   ├── spindleCurrent (REAL): 해당 스핀들의 전류 정보.
    │   │   ├── spindleTemperature (REAL): 해당 스핀들의 온도 정보.
    │   │   ├── rpm/
    │   │   │   # 설명: 스핀들 회전 속도(RPM) 정보.
    │   │   │   ├── commandedSpeed (REAL): 지령된 스핀들 회전 속도.
    │   │   │   ├── actualSpeed (REAL): 실제 측정된 스핀들 회전 속도.
    │   │   │   └── speedUnit (INTEGER): 속도 단위 (2: rpm, 3: mm/rev 등).
    │   │   └── spindlePower/
    │   │       # 설명: 스핀들의 전력 소비량 정보.
    │   │       ├── actualPowerConsumption (REAL): 실 소비 전력의 적산값.
    │   │       ├── powerConsumption (REAL): 소비 전력의 적산값.
    │   │       └── regeneratedPower (REAL): 회생 전력의 적산값.
    │   ├── feed/
    │   │   # 설명: 축 이송 관련 정보.
    │   │   ├── feedOverride (REAL): 가공 이송 속도 오버라이드 비율.
    │   │   ├── rapidOverride (REAL): 급속 이송 속도 오버라이드 비율.
    │   │   └── feedRate/
    │   │       # 설명: 이송 속도(Feedrate) 정보.
    │   │       ├── commandedSpeed (REAL): 지령된 이송 속도.
    │   │       ├── actualSpeed (REAL): 실제 측정된 이송 속도.
    │   │       └── speedUnit (INTEGER): 속도 단위 (0: mm/min, 1: inch/min 등).
    │   ├── workStatus/ **workStatus=k : k번째 작업**
    │   │   # 설명: 가공 작업의 진척 상태에 대한 정보를 담는 리스트 구조.
    │   │   ├── workCounter/
    │   │   │   # 설명: 가공 수량 정보.
    │   │   │   ├── currentWorkCounter (INTEGER): 현재까지 가공한 수량.
    │   │   │   ├── targetWorkCounter (INTEGER): 목표 가공 수량.
    │   │   │   └── totalWorkCounter (INTEGER): 총 가공 수량.
    │   │   └── machiningTime/
    │   │       # 설명: 가공 시간 정보.
    │   │       ├── processingMachiningTime (REAL): 현재 가공이 진행된 시간 (단위: 초).
    │   │       ├── estimatedMachiningTime (REAL): 예상 남은 가공 완료 시간 (SIEMENS 전용).
    │   │       ├── machineOperationTime (REAL): 자동 운전 모드에서의 총 운전 시간 (단위: 초).
    │   │       └── actualCuttingTime (REAL): 실제 총 절삭 시간 (단위: 초).
    │   ├── activeTool/
    │   │   # 설명: 현재 채널에서 활성화(사용 중인)된 공구 정보.
    │   │   ├── locationNumber (INTEGER): 공구가 매거진에 탑재된 위치 번호.
    │   │   ├── toolName (STRING): 공구 이름.
    │   │   ├── toolNumber (INTEGER): 공구 식별 번호 (T 코드).
    │   │   ├── numberOfEdges (INTEGER): 공구 날의 총 개수.
    │   │   ├── toolEnabled (INTEGER): 공구 영역 등록 및 매거진 탑재 여부.
    │   │   ├── magazineNumber (INTEGER): 공구가 탑재된 매거진 번호.
    │   │   ├── sisterToolNumber (INTEGER): 할당된 대체 공구 번호.
    │   │   ├── toolLifeUnit (INTEGER): 공구 수명 측정 단위 기준.
    │   │   ├── toolGroupNumber (INTEGER): 공구가 참조된 공구 그룹 번호 리스트.
    │   │   ├── toolUseOrderNumber (INTEGER): 그룹 내 공구 사용 순서 (FANUC 전용).
    │   │   ├── toolStatus (INTEGER): 공구의 사용 상태.
    │   │   └── toolEdge/
    │   │       # 설명: 현재 활성화된 공구의 날(edge) 정보.
    │   │       ├── edgeNumber (INTEGER): 공구 날 식별 번호.
    │   │       ├── toolType (INTEGER): 공구 유형.
    │   │       ├── lengthOffsetNumber (INTEGER): 공구 길이 보정 식별 번호.
    │   │       ├── geoLengthOffset (REAL): 공구 길이 X 보정값.
    │   │       ├── wearLengthOffset (REAL): 공구 길이 X 마모 보정값.
    │   │       ├── radiusOffsetNumber (INTEGER): 공구 반경 보정 식별 번호.
    │   │       ├── geoRadiusOffset (REAL): 공구 반경 보정값.
    │   │       ├── wearRadiusOffset (REAL): 공구 반경 마모 보정값.
    │   │       ├── edgeEnabled (BOOLEAN): 공구 날 사용 가능 여부.
    │   │       ├── geoLengthOffsetZ (REAL): 공구 길이 Z 보정값.
    │   │       ├── wearLengthOffsetZ (REAL): 공구 길이 Z 마모 보정값.
    │   │       ├── geoLengthOffsetY (REAL): 공구 길이 Y 보정값.
    │   │       ├── wearLengthOffsetY (REAL): 공구 길이 Y 마모 보정값.
    │   │       ├── geoOffsetNumber (INTEGER): 길이 X,Z, 반경의 식별 번호.
    │   │       ├── wearOffsetNumber (INTEGER): 길이 X,Z, 반경 마모값의 식별 번호.
    │   │       ├── cuttingEdgePosition (INTEGER): 공구 인선 방향.
    │   │       ├── tipAngle (REAL): 공구의 팁 각도.
    │   │       ├── holderAngle (REAL): 공구 홀더 각도.
    │   │       ├── insertAngle (REAL): 공구 인서트 각도.
    │   │       ├── insertWidth (REAL): 인선 너비 (SIEMENS 전용).
    │   │       ├── insertLength (REAL): 인선 길이 (SIEMENS 전용).
    │   │       ├── referenceDirectionHolderAngle (REAL): 홀더 각도 참조 방향 (SIEMENS 전용).
    │   │       ├── directionOfSpindleRotation (INTEGER): 스핀들 회전 방향 (SIEMENS 전용).
    │   │       ├── numberOfTeeth (INTEGER): 공구 날 개수 (SIEMENS 전용).
    │   │       └── toolLife/
    │   │           # 설명: 공구 수명 정보.
    │   │           ├── maxToolLife (REAL): 최대 공구 수명.
    │   │           ├── restToolLife (REAL): 잔여 공구 수명.
    │   │           ├── toolLifeCount (REAL): 현재 공구 사용량.
    │   │           └── toolLifeAlarm (REAL): 공구 수명 도달 경고 설정값 (SIEMENS 전용).
    │   ├── currentProgram/
    │   │   # 설명: 현재 실행 중인 NC 프로그램의 상태 정보.
    │   │   ├── sequenceNumber (INTEGER): 현재 실행 중인 시퀀스 번호(N 코드).
    │   │   ├── currentBlockCounter (INTEGER): 실행 중인 블록 카운터.
    │   │   ├── lastBlock (STRING): 이전 블록 정보.
    │   │   ├── currentBlock (STRING): 현재 실행 중인 프로그램 블록 내용.
    │   │   ├── nextBlock (STRING): 다음 블록 정보.
    │   │   ├── activePartProgram (STRING): 실행 중인 프로그램 블록 정보(최대 200자).
    │   │   ├── programMode (INTEGER): 프로그램 실행 모드 (0: Reset, 3: Start 등).
    │   │   ├── currentWorkOffsetIndex (INTEGER): 현재 공작물 좌표계의 G 코드 인덱스.
    │   │   ├── currentWorkOffsetCode (STRING): 현재 공작물 좌표계의 G 코드 문자열.
    │   │   ├── currentDepthLevel (INTEGER): 현재 프로그램의 레벨 (메인, 서브루틴 등).
    │   │   ├── modal/ **modal=k : k번째 G코드 그룹**
    │   │   │   # 설명: G 코드 모달 정보를 담는 리스트.
    │   │   │   ├── modalIndex (INTEGER): G 코드 인덱스.
    │   │   │   └── modalCode (STRING): G 코드 문자열.
    │   │   ├── overallBlock/ **overallBlock=k : k번째 프로그램 레벨**
    │   │   │   # 설명: 실행 중인 블록 정보를 담는 리스트 (SIEMENS 전용).
    │   │   │   ├── blockCounter (INTEGER): 블록 카운터.
    │   │   │   └── programName (STRING): 프로그램 이름.
    │   │   ├── interruptBlock/ **interruptBlock=k : k번째 프로그램 레벨**
    │   │   │   # 설명: 프로그램 중단점 블록 정보를 담는 리스트 (SIEMENS 전용).
    │   │   │   ├── depthLevel (INTEGER): 중단점 블록의 프로그램 레벨.
    │   │   │   ├── blockCounter (INTEGER): 중단점 블록의 카운터.
    │   │   │   ├── programName (STRING): 중단점 블록의 프로그램 이름.
    │   │   │   ├── blockData (STRING): 중단점 블록 데이터.
    │   │   │   ├── searchType (INTEGER): 중단점 검색 유형.
    │   │   │   └── mainProgramName (STRING): 중단점의 메인 프로그램 이름.
    │   │   ├── currentTotalWorkOffset/
    │   │   │   # 설명: 공작물 좌표계의 총 오프셋 정보.
    │   │   │   ├── workOffsetIndex (INTEGER): G 코드 인덱스.
    │   │   │   ├── workOffsetValue **workOffsetValue=k : k번째 축** (REAL): 축별 총 오프셋 값.
    │   │   │   ├── workOffsetRotation **workOffsetRotation=k : k번째 축** (REAL): 축별 총 회전 오프셋 값.
    │   │   │   ├── workOffsetScalingFactor **workOffsetScalingFactor=k : k번째 축** (REAL): 축별 총 스케일링 값.
    │   │   │   └── workOffsetMirroringEnabled **workOffsetMirroringEnabled=k : k번째 축** (BOOLEAN): 축별 미러링 활성화 여부.
    │   │   ├── currentFile/
    │   │   │   # 설명: 현재 실행 중인 프로그램 파일 정보.
    │   │   │   ├── programName (STRING): 파일명.
    │   │   │   ├── programPath (STRING): 파일 경로.
    │   │   │   ├── programSize (REAL): 파일 크기 (byte).
    │   │   │   ├── programDate (STRING): 파일 생성 날짜.
    │   │   │   └── programNameWithPath (STRING): 경로를 포함한 전체 파일명.
    │   │   ├── mainFile/
    │   │   │   # 설명: 현재 선택된(실행 중이 아닐 수 있는) 프로그램 파일 정보.
    │   │   │   ├── programName (STRING): 파일명.
    │   │   │   ├── programPath (STRING): 파일 경로.
    │   │   │   ├── programSize (REAL): 파일 크기 (byte).
    │   │   │   ├── programDate (STRING): 파일 생성 날짜.
    │   │   │   └── programNameWithPath (STRING): 경로를 포함한 전체 파일명.
    │   │   └── controlOption/
    │   │       # 설명: 프로그램 실행 제어 옵션.
    │   │       ├── singleBlock (BOOLEAN): 싱글 블록 실행 여부.
    │   │       ├── dryRun (BOOLEAN): 드라이 런 실행 여부.  
    │   │       ├── optionalStop (BOOLEAN): 옵셔널 스톱(M01) 활성화 여부.
    │   │       ├── blockSkip {blockSkip=k : k번째 블록 스킵 레벨} (BOOLEAN): 블록 스킵 활성화 여부 리스트.
    │   │       └── machineLock (BOOLEAN): 머신 락 활성화 여부.
    │   ├── workOffset/ **workOffset=k : k번째 G코드 인덱스**
    │   │   # 설명: 공작물 좌표계(G54-G59 등)의 오프셋 정보를 담는 리스트 구조.
    │   │   ├── workOffsetValue **workOffsetValue=l : l번째 축** (REAL): G 코드 인덱스에 대한 축별 오프셋 값.
    │   │   ├── workOffsetRotation **workOffsetRotation=l : l번째 축** (REAL): 축별 오프셋 회전량 (SIEMENS 전용).
    │   │   ├── workOffsetScalingFactor **workOffsetScalingFactor=l : l번째 축** (REAL): 축별 오프셋 확장량 (SIEMENS 전용).
    │   │   ├── workOffsetMirroringEnabled **workOffsetMirroringEnabled=l : l번째 축** (BOOLEAN): 축별 미러링 활성화 여부 (SIEMENS 전용).
    │   │   └── workOffsetFine **workOffsetFine=l : l번째 축** (REAL): 축별 오프셋 Fine 값 (SIEMENS 전용).
    │   ├── alarm/ **alarm=k : k번째 알람**
    │   │   # 설명: 발생한 알람 정보를 담는 리스트 구조.
    │   │   ├── alarmText (STRING): 알람 상세 내용.
    │   │   ├── alarmCategory (STRING): 알람 유형.
    │   │   ├── alarmNumber (STRING): 알람 번호.
    │   │   └── raisedTimeStamp (STRING): 알람 발생 시각.
    │   └── variable/ **variable=k : k번째 사용자 변수**
    │       # 설명: 사용자 변수(매크로 변수)를 담는 리스트 구조.
    │       └── userVariable (REAL): 사용자 변수 값.
    ├── pic/
    │   # 설명: CNC 내부 PLC 메모리 데이터 모델.
    │   └── memory/
    │       ├── rbitBlock/ **rbitBlock=j : j번째 주소** (BOOLEAN): 읽기 전용 Bit 데이터 블록.
    │       ├── bitBlock/ **bitBlock=j : j번째 주소** (BOOLEAN): 읽기/쓰기 가능 Bit 데이터 블록.
    │       ├── rbyteBlock/ **rbyteBlock=j : j번째 주소** (BYTE): 읽기 전용 Byte 데이터 블록.
    │       ├── byteBlock/ **byteBlock=j : j번째 주소** (BYTE): 읽기/쓰기 가능 Byte 데이터 블록.
    │       ├── rwordBlock/ **rwordBlock=j : j번째 주소** (WORD): 읽기 전용 Word(2byte) 데이터 블록.
    │       ├── wordBlock/ **wordBlock=j : j번째 주소** (WORD): 읽기/쓰기 가능 Word(2byte) 데이터 블록.
    │       ├── rdwordBlock/ **rdwordBlock=j : j번째 주소** (DWORD): 읽기 전용 DWord(4byte) 데이터 블록.
    │       ├── dwordBlock/ **dwordBlock=j : j번째 주소** (DWORD): 읽기/쓰기 가능 DWord(4byte) 데이터 블록.
    │       ├── rqwordBlock/ **rqwordBlock=j : j번째 주소** (QWORD): 읽기 전용 QWord(8byte) 데이터 블록.
    │       └── qwordBlock/ **qwordBlock=j : j번째 주소** (QWORD): 읽기/쓰기 가능 QWord(8byte) 데이터 블록.
    ├── toolArea/ **toolArea=j : j번째 공구 영역**
    │   # 설명: 장비의 공구 영역(매거진, 공구 목록 등)에 대한 정보를 담는 리스트 구조.
    │   ├── toolAreaEnabled (BOOLEAN): 해당 공구 영역 사용 가능 여부.
    │   ├── numberOfMagazines (INTEGER): 사용 가능한 매거진 개수.
    │   ├── numberOfRegisteredTools (INTEGER): 공구 영역에 등록된 총 공구 개수.
    │   ├── numberOfLoadedTools (INTEGER): 매거진에 탑재된 총 공구 개수.
    │   ├── numberOfToolGroups (INTEGER): 등록된 공구 그룹의 개수.
    │   ├── numberOfToolOffsets (INTEGER): 등록된 공구 오프셋의 개수.
    │   ├── magazine/ **magazine=k : k번째 매거진**
    │   │   # 설명: 매거진 정보를 담는 리스트 구조.
    │   │   ├── magazineEnabled (BOOLEAN): 해당 매거진 사용 가능 여부.
    │   │   ├── magazineName (STRING): 매거진 이름 (SIEMENS 전용).
    │   │   ├── numberOfRealLocations (INTEGER): 매거진의 물리적 포트(위치) 개수.
    │   │   ├── magazinePhysicalNumber (INTEGER): 매거진의 물리적 번호.
    │   │   └── numberOfLoadedTools (INTEGER): 해당 매거진에 탑재된 공구 개수.
    │   ├── tools/ **tools=k : k번째 공구 번호**
    │   │   # 설명: 공구 번호를 기준으로 조회하는 공구 정보 리스트 (대부분 읽기/쓰기 가능).
    │   │   ├── locationNumber (INTEGER): 공구가 매거진에 탑재된 위치 번호.
    │   │   ├── toolName (STRING): 공구 이름.
    │   │   ├── numberOfEdges (INTEGER): 공구 날의 총 개수.
    │   │   ├── toolEnabled (INTEGER): 공구 영역 등록 및 매거진 탑재 여부.
    │   │   ├── magazineNumber (INTEGER): 공구가 탑재된 매거진 번호.
    │   │   ├── sisterToolNumber (INTEGER): 할당된 대체 공구 번호.
    │   │   ├── toolLifeUnit (INTEGER): 공구 수명 측정 단위 기준.
    │   │   ├── toolGroupNumber (LIST[INTEGER]): 공구가 참조된 공구 그룹 번호 리스트.
    │   │   ├── toolUseOrderNumber (INTEGER): 그룹 내 공구 사용 순서 (FANUC 전용).
    │   │   ├── toolStatus (INTEGER): 공구의 사용 상태.
    │   │   └── toolEdge/ **toolEdge=l : l번째 공구 날**
    │   │       # 설명: 공구 날(edge) 정보를 담는 리스트.
    │   │       ├── toolType (INTEGER): 공구 유형.
    │   │       ├── lengthOffsetNumber (INTEGER): 공구 길이 보정 식별 번호.**lengthOffsetNumber=m : m번째 공구 그룹**
    │   │       ├── geoLengthOffset (REAL): 공구 길이 X 보정값.**geoLengthOffset=m : m번째 공구 그룹**
    │   │       ├── wearLengthOffset (REAL): 공구 길이 X 마모 보정값.**wearLengthOffset=m : m번째 공구 그룹**
    │   │       ├── radiusOffsetNumber (INTEGER): 공구 반경 보정 식별 번호.**radiusOffsetNumber=m : m번째 공구 그룹**
    │   │       ├── geoRadiusOffset (REAL): 공구 반경 보정값.**geoRadiusOffset=m : m번째 공구 그룹**
    │   │       ├── wearRadiusOffset (REAL): 공구 반경 마모 보정값. **wearRadiusOffset=m : m번째 공구 그룹**
    │   │       ├── edgeEnabled (BOOLEAN): 공구 날 사용 가능 여부.
    │   │       ├── geoLengthOffsetZ (REAL): 공구 길이 Z 보정값.**geoLengthOffsetZ=m : m번째 공구 그룹**
    │   │       ├── wearLengthOffsetZ (REAL): 공구 길이 Z 마모 보정값.**wearLengthOffsetZ=m : m번째 공구 그룹**
    │   │       ├── geoLengthOffsetY (REAL): 공구 길이 Y 보정값. **geoLengthOffsetY=m : m번째 공구 그룹**
    │   │       ├── wearLengthOffsetY (REAL): 공구 길이 Y 마모 보정값.**wearLengthOffsetY=m : m번째 공구 그룹**
    │   │       ├── geoOffsetNumber (INTEGER): 길이 X,Z, 반경의 식별 번호.**geoOffsetNumber=m : m번째 공구 그룹**
    │   │       ├── wearOffsetNumber (INTEGER): 길이 X,Z, 반경 마모값의 식별 번호. **wearOffsetNumber=m : m번째 공구 그룹**
    │   │       ├── cuttingEdgePosition (INTEGER): 공구 인선 방향.**cuttingEdgePosition=m : m번째 공구 그룹**
    │   │       ├── tipAngle (REAL): 공구의 팁 각도.
    │   │       ├── holderAngle (REAL): 공구 홀더 각도.
    │   │       ├── insertAngle (REAL): 공구 인서트 각도.
    │   │       ├── insertWidth (REAL): 인선 너비 (SIEMENS 전용).
    │   │       ├── insertLength (REAL): 인선 길이 (SIEMENS 전용).
    │   │       ├── referenceDirectionHolderAngle (REAL): 홀더 각도 참조 방향 (SIEMENS 전용).
    │   │       ├── directionOfSpindleRotation (INTEGER): 스핀들 회전 방향 (SIEMENS 전용).
    │   │       ├── numberOfTeeth (INTEGER): 공구 날 개수 (SIEMENS 전용).
    │   │       └── toolLife/
    │   │           # 설명: 공구 수명 정보 (읽기/쓰기 가능).
    │   │           ├── maxToolLife (REAL): 최대 공구 수명. **maxToolLife = m : m번째 공구 그룹**
    │   │           ├── restToolLife (REAL): 잔여 공구 수명. **restToolLife = m : m번째 공구 그룹**
    │   │           ├── toolLifeCount (REAL): 현재 공구 사용량. **toolLifeCount = m : m번째 공구 그룹**
    │   │           └── toolLifeAlarm (REAL): 공구 수명 도달 경고 설정값.
    │   └── registerTools/ **registerTools=k : k번째 인덱스**
    │       # 설명: NC에 등록된 순서(인덱스) 기준의 공구 정보 리스트 (대부분 읽기/쓰기 가능).
    │       ├── locationNumber (INTEGER): 공구가 매거진에 탑재된 위치 번호.
    │       ├── toolName (STRING): 공구 이름.
    │       ├── numberOfEdges (INTEGER): 공구 날의 총 개수.
    │       ├── toolEnabled (INTEGER): 공구 영역 등록 및 매거진 탑재 여부.
    │       ├── magazineNumber (INTEGER): 공구가 탑재된 매거진 번호.
    │       ├── sisterToolNumber (INTEGER): 할당된 대체 공구 번호.
    │       ├── toolLifeUnit (INTEGER): 공구 수명 측정 단위 기준.
    │       ├── toolGroupNumber (LIST[INTEGER]): 공구가 참조된 공구 그룹 번호 리스트.
    │       ├── toolUseOrderNumber (INTEGER): 그룹 내 공구 사용 순서 (FANUC 전용).
    │       ├── toolStatus (INTEGER): 공구의 사용 상태.
    │       └── toolEdge/ **toolEdge=l : l번째 공구 날**
    │           # 설명: 공구 날(edge) 정보를 담는 리스트.
    │           ├── toolType (INTEGER): 공구 유형.
    │           ├── lengthOffsetNumber (INTEGER): 공구 길이 보정 식별 번호. **lengthOffsetNumber=m : m번째 공구 그룹**
    │           ├── geoLengthOffset (REAL): 공구 길이 X 보정값. **geoLengthOffset=m : m번째 공구 그룹**
    │           ├── wearLengthOffset (REAL): 공구 길이 X 마모 보정값.**wearLengthOffset=m : m번째 공구 그룹**
    │           ├── radiusOffsetNumber (INTEGER): 공구 반경 보정 식별 번호. **radiusOffsetNumber=m : m번째 공구 그룹**
    │           ├── geoRadiusOffset (REAL): 공구 반경 보정값.**geoRadiusOffset=m : m번째 공구 그룹**
    │           ├── wearRadiusOffset (REAL): 공구 반경 마모 보정값.**wearRadiusOffset=m : m번째 공구 그룹**
    │           ├── edgeEnabled (BOOLEAN): 공구 날 사용 가능 여부.
    │           ├── geoLengthOffsetZ (REAL): 공구 길이 Z 보정값. **geoLengthOffsetZ=m : m번째 공구 그룹**
    │           ├── wearLengthOffsetZ (REAL): 공구 길이 Z 마모 보정값. **wearLengthOffsetZ=m : m번째 공구 그룹**
    │           ├── geoLengthOffsetY (REAL): 공구 길이 Y 보정값. **geoLengthOffsetY=m : m번째 공구 그룹**
    │           ├── wearLengthOffsetY (REAL): 공구 길이 Y 마모 보정값.**wearLengthOffsetY=m : m번째 공구 그룹**
    │           ├── geoOffsetNumber (INTEGER): 길이 X,Z, 반경의 식별 번호. **geoOffsetNumber=m : m번째 공구 그룹**
    │           ├── wearOffsetNumber (INTEGER): 길이 X,Z, 반경 마모값의 식별 번호. **wearOffsetNumber=m : m번째 공구 그룹**
    │           ├── cuttingEdgePosition (INTEGER): 공구 인선 방향. **cuttingEdgePosition=m : m번째 공구 그룹**
    │           ├── tipAngle (REAL): 공구의 팁 각도.
    │           ├── holderAngle (REAL): 공구 홀더 각도.
    │           ├── insertAngle (REAL): 공구 인서트 각도.
    │           ├── insertWidth (REAL): 인선 너비 (SIEMENS 전용).
    │           ├── insertLength (REAL): 인선 길이 (SIEMENS 전용).
    │           ├── referenceDirectionHolderAngle (REAL): 홀더 각도 참조 방향 (SIEMENS 전용).
    │           ├── directionOfSpindleRotation (INTEGER): 스핀들 회전 방향 (SIEMENS 전용).
    │           ├── numberOfTeeth (INTEGER): 공구 날 개수 (SIEMENS 전용).
    │           └── toolLife/
    │               # 설명: 공구 수명 정보 (읽기/쓰기 가능).
    │               ├── maxToolLife (REAL): 최대 공구 수명. **maxToolLife = m : m번째 공구 그룹**
    │               ├── restToolLife (REAL): 잔여 공구 수명.**restToolLife = m : m번째 공구 그룹**
    │               ├── toolLifeCount (REAL): 현재 공구 사용량. **toolLifeCount = m : m번째 공구 그룹**
    │               └── toolLifeAlarm (REAL): 공구 수명 도달 경고 설정값.
    └── buffer/ **buffer=j : j번째 버퍼**
        # 설명: 내장 센서 데이터의 시계열 수집(Time-series) 정보를 담는 리스트 구조 (KCNC, FANUC만 지원).
        ├── bufferEnabled (BOOLEAN): 해당 버퍼 사용 가능 여부.
        ├── numberOfStream (INTEGER): 해당 버퍼의 최대 스트림 개수.
        ├── statusOfStream (INTEGER): 스트림 상태 (0: 설정 가능, 3: 수집 중 등).
        ├── modOfStream (INTEGER): 스트림 수집 모드 (0: 반복 수집, 1: 1회 수집).
        ├── machineChannelOfStream (INTEGER): 스트림 수집 시 사용할 채널.
        ├── periodOfStream (INTEGER): 1회 수집 기간 (단위: ms).
        ├── triggerOfStream (INTEGER): 수집 시작 트리거 (0: 즉시, 1이상: 시퀀스 번호).
        ├── frequencyOfStream (INTEGER): 모든 스트림에 공통으로 적용할 수집 주파수 (Hz).
        └── stream/ **stream=k : k번째 스트림**
             # 설명: 개별 센서 데이터 스트림 채널에 대한 설정 및 마지막 값.
             ├── streamEnabled (BOOLEAN): 해당 스트림 사용 가능 여부.
             ├── streamFrequency (INTEGER): 해당 스트림의 수집 주파수 (Hz).
             ├── streamCategory (INTEGER): 수집 대상 데이터 카테고리.
             ├── streamSubcategory (INTEGER): 수집 대상 데이터 서브카테고리 (축/스핀들 번호 등).
             ├── streamType (INTEGER): 수집 유형 (KCNC 전용).
             ├── streamStartBit (INTEGER): 수집 유형이 Bit일 때 Start Bit (KCNC 전용).
             ├── streamEndBit (INTEGER): 수집 유형이 Bit일 때 End Bit (KCNC 전용).
             └── value (REAL): 해당 스트림에서 마지막으로 수집된 데이터 값.
             
             
             
[Torus platform 에러코드 모음]
**User API 및 플랫폼 내부 모듈 오류 코드**
TORUS Platform의 User API 및 플랫폼 내부 모듈에서 발생하는 오류 코드는 다음과 같습니다.

[분류]         [오류 코드(16진수)]  [오류 코드(10진수)]  [설명]
Manager        0X2020500D           538988557            MgrCommunication 시뮬 버전 오류
Manager        0X20206003           538992643            MgrCommunication 파라미터 Query 오류
Manager        0X20206009           538992649            MgrCommunication Address parsing 오류
Manager        0X20206011           538992657            MgrCommunication 유효하지 않은 updatedata의 data 오류
Manager        0X20206012           538992658            MgrCommunication 존재하지 않는 구독 오류
Manager        0X20206013           538992659            MgrCommunication 존재하지 않는 Timeseries 오류
Manager        0X20206028           538992680            MgrCommunication Address 또는 Filter 오류
Manager        0X20207013           538996755            StateModel 존재하지 않는 Timeseries 오류
Manager        0X20102004           537927684            MgrApplication AppInfo 로딩 오류
Manager        0X20102005           537927685            MgrApplication Filter Appname 표기 오류
Manager        0X20102006           537927686            MgrApplication Address에 AppName 속성이 존재하지 않는 오류
Manager        0X20102007           537927687            MgrApplication Address에 AppID 속성이 존재하지 않는 오류
Manager        0X20102008           537927688            MgrApplication App RpcClient 생성 오류
Manager        0X20304009           540033033            MgrCommand Address parsing 오류
Manager        0X2030400A           540033034            MgrCommand 정의되지 않음 Address 공급자 오류
Manager        0X20604009           543178761            MgrLog Address parsing 오류
UserAPI        0X20B00001           548405249            Initialize 중복 시도 오류
UserAPI        0X20B00009           548405257            Address parsing 오류
UserAPI        0X20B00025           548405285            Initialize 오류
UserAPI        0X20B00028           548405288            Address 또는 Filter 오류
UserAPI        0X20B0002A           548405290            Address 결과값 Type 오류
UserAPI        0X20B00032           548405298            알수 없는 구독 설정 오류
UserAPI        0X20B00034           548405300            Null Pointer 오류
Library        0X20D00016           550502422            LibAddress Split command 오류
Library        0X20D00017           550502423            LibAddress XAddress parsing 오류
Library        0X20D00018           550502424            LibAddress Address Code 변환 오류
Library        0X20E00019           551551001            LibAppinfo RpcClient Set 오류
Library        0X20E0001A           551551002            LibAppinfo App Info Set 오류
Library        0X20E0001B           551551003            LibAppinfo AppInfo Load 오류
Library        0X2150001C           558891036            LibRpcClient Connect 오류
Library        0X2150002F           558891055            LibRpcClient TimeOut 오류
Library        0X21500030           558891056            LibRpcClient Canceled 오류
Library        0X21500031           558891057            LibRpcClient Grpc 에서 알수 없는 오류
Library        0X21A00022           564133922            LibSharedMap Platform Version 오류
Library        0X21A00023           564133923            LibSharedMap Icon Name 오류
Library        0X21A00024           564133924            LibSharedMap WatchDog Set 오류
Library        0X21A00025           564133925            LibSharedMap Initialize 오류
Library        0X21A00026           564133926            LibSharedMap Push Range 오류
Library        0X21A0002B           564133931            LibSharedMap Icon Path 오류
Library        0X21A0002C           564133932            LibSharedMap App Version 오류
Library        0X21A0002E           564133934            LibSharedMap App ProviderName 오류



** NC 통신 관련 오류 코드 **

TORUS Platform의 NC 통신 부분에서 발생하는 오류 코드는 다음과 같습니다.

[분류]                      [에러 명]                                [에러 코드(10진수)] [에러 코드(16진수)] [설명]
--------------------------------------------------------------------------------
CNC 통신                    NC_ERR_DUPLICATED_WRITER                 565510144           0x21B50000          한번의 Write 명령에서 동일한 address와 동일한 filter값으로 두 번 이상 값을 쓰려고 할 때 발생
CNC 통신                    NC_ERR_CONNET_FAIL                       565575680           0x21B60000          NC와의 통신에 실패
CNC 통신                    NC_ERR_NO_MACHINE                        565579776           0x21B61000          접속할 NC정보가 없는데 접속을 시도한 경우
CNC 통신                    NC_ERR_NO_CONNET_TRY                     565583872           0x21B62000          접속 시도를 한적이 없는데 ReadWrite를 시도한 경우
CNC 통신                    NC_ERR_NO_FUNCTION                       565641216           0x21B70000          해당 NC에서는 지원하지 않는 기능 (지원하지만 구현되어 있지 않은 기능 포함)
CNC 통신                    NC_ERR_NO_OPTION                         565706752           0x21B80000          해당 NC의 옵션에서는 지원하지 않는 기능
CNC 통신                    NC_ERR_NO_DLL                            565710848           0x21B81000          해당 기능에 필요한 DLL이 없는 경우
CNC 통신                    NC_ERR_NO_HANDLE                         565714944           0x21B82000          해당 NC와의 통신 중에 HANDLE에 문제가 발생한 경우
CNC 통신                    NC_ERR_NO_ACTIVE_TOOL_OR_TOOL_GROUP      565719040           0x21B83000          활성화된 공구 혹은 공구 그룹이 없는 경우
CNC 통신                    NC_ERR_WRONG_TOOL_SYSTEM                 565723136           0x21B84000          TOOL SYSTEM 설정이 실제와 맞지 않는 경우
CNC 통신                    NC_ERR_NO_TOOL_GROUP                     565727232           0x21B85000          해당 공구 그룹이 없는 경우
CNC 통신                    NC_ERR_NO_SELECETD_FILE                  565731328           0x21B86000          메인 혹은 서브 프로그램이 존재하지 않아서 정보를 읽어올수 없는 경우
CNC 통신                    NC_ERR_INVALID_WRITE_VALUE               565772288           0x21B90000          허용되지 않는 WRITE값을 입력한 경우
CNC 통신                    NC_ERR_WRONG_WRITE_VALUE_LIST_COUNT      565776384           0x21B91000          쓰기 값의 수량이 filter값에 입력된 수량과 다른 경우
CNC 통신                    NC_ERR_INAPPROPRIATE_STATUS              565780480           0x21B92000          현재 상태에서는 불가능한 작업인 경우
CNC 통신                    NC_ERR_WRONG_FILTER_VALUE                565837824           0x21BA0000          입력한 filter값 중 일부 혹은 전체가 잘못 되었음
CNC 통신                    NC_ERR_UNKNOWN                           565903360           0x21BB0000          알 수 없는 오류(주로 해당 Vendor의 오류값 중 해석되지 않은 오류)
CNC 통신                    NC_ERR_NO_OBJECT_IN_NC                   565972992           0x21BC1000          NC의 해당 경로에 해당 객체가 없는 경우
CNC 통신                    NC_ERR_NO_OBJECT_IN_LOCAL                565973248           0x21BC1100          LOCAL의 해당 경로에 해당 객체가 없는 경우
CNC 통신                    NC_ERR_WRONG_PATH_IN_NC                  565973504           0x21BC1200          파일 복사나 이동시 목적지(NC)의 경로가 없는 경로인 경우입니다. (복사나 이동 목적지 폴더가 존재하지 않는 경우)
CNC 통신                    NC_ERR_WRONG_PATH_IN_LOCAL               565973760           0x21BC1300          파일 복사나 이동시 목적지(LOCAL)의 경로가 없는 경로인 경우입니다. (복사나 이동 목적지 폴더가 존재하지 않는 경우)
CNC 통신                    NC_ERR_OBJECT_AREADY_EXIST_IN_NC         565977088           0x21BC2000          NC의 해당 경로에 이미 같은 이름의 객체가 있는 경우
CNC 통신                    NC_ERR_OBJECT_AREADY_EXIST_IN_LOCAL      565977344           0x21BC2100          LOCAL의 해당 경로에 이미 같은 이름의 객체가 있는 경우
CNC 통신                    NC_ERR_FAIL_CREATE_OBJECT_IN_NC          565981184           0x21BC3000          NC의 해당 경로에 객체를 생성하는데 실패한 경우
CNC 통신                    NC_ERR_FAIL_CREATE_OBJECT_IN_LOCAL       565981440           0x21BC3100          LOCAL의 해당 경로에 객체를 생성하는데 실패한 경우
CNC 통신                    NC_ERR_OBJECT_IS_USED_IN_NC              565985280           0x21BC4000          NC의 해당 객체가 사용중인 경우
CNC 통신                    NC_ERR_OBJECT_IS_USED_IN_LOCAL           565985536           0x21BC4100          LOCAL의 해당 객체가 사용중인 경우
CNC 통신                    NC_ERR_STORAGE_SHORTAGE_IN_NC            565989376           0x21BC5000          NC의 용량이 부족한 경우
CNC 통신                    NC_ERR_WRONG_NC_FILE                     565993472           0x21BC6000          NC 파일 내용이 형식에 맞지 않는 경우
CNC 통신                    NC_ERR_WRONG_NAME_OF_NC_FILE             565993728           0x21BC6100          NC 파일 이름 형식이 CNC 형식과 맞지 않는 경우 (KCNC의 경우 NC파일의 확장자가 ".nc"여야 합니다.)
CNC 통신                    NC_ERR_FAIL_OPEN_OBJECT_IN_NC            565997568           0x21BC7000          NC의 해당 경로에 있는 파일을 열지 못한 경우
CNC 통신                    NC_ERR_FAIL_OPEN_OBJECT_IN_LOCAL         565997824           0x21BC7100          LOCAL의 해당 경로에 있는 파일을 열지 못한 경우
CNC 통신                    NC_ERR_WRONG_RETURN_DATA_TYPE            566034432           0x21BD0000          반환 데이터가 MachineStateModel의 데이터 타입과 맞지 않는 경우
CNC 통신                    NC_ERR_NULL_VALUE                        566099968           0x21BE0000          해당 값이 NULL 값인 경우
CNC 통신                    NC_OK                                    0                   0x0                 정상
NC 내부 PLC 데이터 통신       -                                        548438071           0x20b08037          Memory mapping file 정보 읽기 실패
NC 내부 PLC 데이터 통신       CODE_ERROR_ADDRESS_OR_FILTER             548442152           0x20b09028          mapping table에 target Data type이 잘못 설정되어 있는 경우
NC 내부 PLC 데이터 통신       CODE_ERROR_PARSING_ADDRES                548442165           0x20b09035          Memory mapping table에 없는 어드레스를 읽거나 쓰려고 할 때
NC 내부 PLC 데이터 통신       CODE_ERROR_PARSING_FILTER                548442166           0x20b09036          Memory mapping table에 데이터 어드레스 범위 표기가 잘못되어 있거나 getData, updateData 함수 호출 시 입력하는 어드레스 필터 정보에 어드레스 범위가 잘못 지정되어 있는 경우
NC 내부 PLC 데이터 통신       CODE_ERROR_MEM_MAP_FILE                  548442167           0x20b09037          Memory mapping table의 NC internal PLC 측 데이터 어드레스 지정 부분에 잘못된 표기가 포함된 경우
NC 내부 PLC 데이터 통신       CODE_ERROR_MEM_MAPPING                   548442168           0x20b09038          Memory mapping table에 필수 설정해야 할 항목이 빠져 있는 경우



** 비가공장비 통신 관련 오류 코드 **

비 가공장비 통신 부분의 오류 코드에 대한 설명은 다음과 같습니다.

[분류]                      [오류 코드(10진수)]  [오류 코드(16진수)]  [설명]
--------------------------------------------------------------------------------
통신 Manager                566235137            0x21C01001           요청한 데이터 어드레스에 필터가 지정되어 있지 않습니다.
통신 Manager                566235138            0x21C01002           요청한 데이터 어드레스에 "DIRECT" 플래그가 지정되어 있지 않습니다.
통신 Manager                566235139            0x21C01003           bit type 데이터 쓰기 지령 시, 오류 발생했습니다.
통신 Manager                566235140            0x21C01004           word type 데이터 쓰기 지령 시, 오류 발생했습니다.
통신 Manager                566235141            0x21C01005           비 가공장비 통신 매니저 등록정보 파일에 오류가 있습니다.
통신 Manager                566235142            0x21C01006           비 가공장비 통신 프로토콜 등록정보 파일에 오류가 있습니다.
통신 Manager                566235147            0x21C0100B           비 가공장비 리스트 파일이 없습니다.
통신 Manager                566235148            0x21C0100C           비 가공장비 리스트 파일 내에 잘못 기입된 정보가 있거나, 요소 정보가 없습니다.
통신 Manager                566235149            0x21C0100D           비 가공장비 리스트 파일 내에 Device ID가 중복되는 내용이 있습니다.
통신 Manager                297799687            0x11C01007           저장된 로그가 없습니다.
통신 Manager                297799689            0x11C01009           요청한 데이터 어드레스 내의 필터가 잘못되었습니다.
통신 Manager                297799690            0x11C0100A           쓰기 요청한 데이터의 타입 지정이 잘못 되었습니다.
통신 Manager                297799688            0x11C01008           쓰기 지령에 사용한 데이터 어드레스에 필터가 지정되어 있지 않습니다.
통신 Library (MODBUS TCP)    567287837            0x21D0201D           MODBUS TCP 통신 연결에 실패 했습니다.
통신 Library (MODBUS TCP)    567287836            0x21D0201C           MODBUS TCP 통신 설정에 오류가 있습니다.
통신 Library (MODBUS TCP)    567287835            0x21D0201B           MODBUS TCP 통신 객체 생성에 실패했습니다.
통신 Library (MODBUS TCP)    567296021            0x21D04015           어드레스의 길이가 잘못되었습니다.
통신 Library (MODBUS TCP)    567287841            0x21D02021           알 수 없는 오류가 발생했습니다. TORUS Platform 웹사이트에 문의하세요
통신 Library (MODBUS TCP)    567287810            0x21D02002           MODBUS TCP 통신 객체가 존재하지 않습니다.
통신 Library (MODBUS TCP)    567287809            0x21D02001           장치에서 정보 읽기가 실패했습니다.
통신 Library (MODBUS TCP)    567287833            0x21D02019           장치의 읽기/쓰기 실패했습니다.
통신 Library (MODBUS TCP)    1104158723           0x41D02003           MODBUS TCP 객체 소멸 시 오류가 발생했습니다.
통신 Library (MODBUS TCP)    1104158725           0x41D02005           메모리 해제에 실패했습니다.
통신 Library (MODBUS TCP)    567287834            0x21D0201A           장치가 존재하지 않습니다.