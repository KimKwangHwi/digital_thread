[URI 생성 예시]
장비 모델명 조회
data://machine/cncModel?machine=1

첫 번째 장비의 첫 번째 채널, 두 번째 축의 부하 조회
data://machine/channel/axis/axisLoad?machine=1&channel=1&axis=2

첫 번째 장비의 첫 번째 채널, 첫 번째 스핀들의 소비 전력 조회
data://machine/channel/spindle/spindlePower/powerConsumption?machine=1&channel=1&spindle=1


### 데이터 모델 계층 구조, 각 데이터 설명, 필요 파라미터

<?xml version="1.0" encoding="UTF-8"?>
<schema title="TORUS Platform Machine Data Model" description="TORUS Platform의 전체 데이터 모델에 대한 XML 스키마입니다. 제공된 목록에 따라 특정 속성은 array 타입으로 정의되었습니다.">
  <properties>
    <property name="machine">
      <type>array</type>
      <description>단위 공작기계의 리스트. 필터 `machine=i`를 사용하여 특정 장비를 식별합니다.</description>
      <items>
        <type>object</type>
        <properties>
          <property name="cncModel">
            <type>string</type>
            <description>해당 장비에 탑재된 NC의 모델명.</description>
          </property>
          <property name="numberOfChannels">
            <type>integer</type>
            <description>장비에서 사용 가능한 채널(계통)의 개수.</description>
          </property>
          <property name="cncVendor">
            <type>integer</type>
            <description>NC 제조사 코드 (1: FANUC, 2: SIEMENS, 3: CSCAM, 4: MITSUBISHI, 5: KCNC).</description>
          </property>
          <property name="ncLinkState">
            <type>boolean</type>
            <description>NC와의 통신 연결 상태.</description>
          </property>
          <property name="currentAccessLevel">
            <type>integer</type>
            <description>프로그램/디렉토리 접근에 대한 사용 권한 수준 (SIEMENS 전용, 1~7단계).</description>
          </property>
          <property name="basicLengthUnit">
            <type>integer</type>
            <description>장비가 사용하는 기본 길이 단위 (0: Metric, 1: Inches 등).</description>
          </property>
          <property name="machinePowerOnTime">
            <type>number</type>
            <description>장비의 전원이 켜진 시간 (단위: 분).</description>
          </property>
          <property name="currentCncTime">
            <type>string</type>
            <format>date-time</format>
            <description>장비에 설정된 현재 시각 (형식: yyyy-MM-ddTHH:mm:ss).</description>
          </property>
          <property name="machineType">
            <type>integer</type>
            <description>장비의 타입 (1: Milling, 2: Lathe 등).</description>
          </property>
          <property name="ncMemory">
            <type>object</type>
            <description>NC 프로그램 저장 메모리 용량에 관한 정보를 포함합니다.</description>
            <properties>
              <property name="totalCapacity">
                <type>number</type>
                <description>NC 메모리의 전체 용량 (단위: byte).</description>
              </property>
              <property name="usedCapacity">
                <type>number</type>
                <description>사용 중인 NC 메모리 용량 (단위: byte).</description>
              </property>
              <property name="freeCapacity">
                <type>number</type>
                <description>NC 메모리의 남은 용량 (단위: byte).</description>
              </property>
              <property name="rootPath">
                <type>string</type>
                <description>NC 메모리의 기본(루트) 경로.</description>
              </property>
            </properties>
          </property>
          <property name="channel">
            <type>array</type>
            <description>채널 별 상태 정보 리스트. {channel=j}</description>
            <items>
              <type>object</type>
              <properties>
                <property name="channelEnabled">
                  <type>boolean</type>
                  <description>해당 채널의 활성화 여부.</description>
                </property>
                <property name="toolAreaNumber">
                  <type>integer</type>
                  <description>해당 채널에서 사용 가능한 공구 영역의 식별 번호.</description>
                </property>
                <property name="numberOfAxes">
                  <type>integer</type>
                  <description>해당 채널에서 사용 가능한 축의 개수.</description>
                </property>
                <property name="numberOfSpindles">
                  <type>integer</type>
                  <description>해당 채널에서 사용 가능한 스핀들의 개수.</description>
                </property>
                <property name="alarmStatus">
                  <type>integer</type>
                  <description>채널의 알람 상태 (0: No alarm, 1: Alarm 등).</description>
                </property>
                <property name="numberOfAlarms">
                  <type>integer</type>
                  <description>해당 채널에서 발생한 알람의 총 개수.</description>
                </property>
                <property name="operateMode">
                  <type>integer</type>
                  <description>공작기계의 운전 모드 (0: JOG, 1: MDI, 2: MEMORY 등).</description>
                </property>
                <property name="numberOfWorkOffsets">
                  <type>integer</type>
                  <description>사용 가능한 공작물 좌표계의 개수.</description>
                </property>
                <property name="ncState">
                  <type>integer</type>
                  <description>CNC의 작동 상태 (0: Reset, 1: Stop, 2: Hold, 3: Start 등).</description>
                </property>
                <property name="motionStatus">
                  <type>integer</type>
                  <description>장비의 현재 모션 상태 (1: Motion, 2: Dwell 등).</description>
                </property>
                <property name="emergencyStatus">
                  <type>integer</type>
                  <description>비상 정지(Emergency) 상태 여부 (0: Not emergency, 1: Emergency).</description>
                </property>
                <property name="axis">
                  <type>array</type>
                  <description>축 별 상태 정보 리스트. {axis=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="machinePosition">
                        <type>number</type>
                        <description>기계 좌표계 기준 현재 위치.</description>
                      </property>
                      <property name="workPosition">
                        <type>number</type>
                        <description>공작물 좌표계 기준 현재 위치.</description>
                      </property>
                      <property name="distanceToGo">
                        <type>number</type>
                        <description>지령 위치까지 남은 이동 거리.</description>
                      </property>
                      <property name="relativePosition">
                        <type>number</type>
                        <description>상대 좌표계 기준 현재 위치.</description>
                      </property>
                      <property name="axisName">
                        <type>string</type>
                        <description>절대 좌표계의 축 이름.</description>
                      </property>
                      <property name="relativeAxisName">
                        <type>string</type>
                        <description>상대 좌표계의 축 이름 (FANUC 전용).</description>
                      </property>
                      <property name="axisLoad">
                        <type>number</type>
                        <description>축에 걸리는 부하.</description>
                      </property>
                      <property name="axisFeed">
                        <type>number</type>
                        <description>현재 축의 이송 속도.</description>
                      </property>
                      <property name="axisLimitPlus">
                        <type>number</type>
                        <description>'+' 방향 최대 이동 한계값.</description>
                      </property>
                      <property name="axisLimitMinus">
                        <type>number</type>
                        <description>'-' 방향 최대 이동 한계값.</description>
                      </property>
                      <property name="workAreaLimitPlus">
                        <type>number</type>
                        <description>작업 금지 영역 '+' 방향 한계값.</description>
                      </property>
                      <property name="workAreaLimitMinus">
                        <type>number</type>
                        <description>작업 금지 영역 '-' 방향 한계값.</description>
                      </property>
                      <property name="workAreaLimitPlusEnabled">
                        <type>boolean</type>
                        <description>작업 금지 영역 '+' 방향 활성화 여부.</description>
                      </property>
                      <property name="workAreaLimitMinusEnabled">
                        <type>boolean</type>
                        <description>작업 금지 영역 '-' 방향 활성화 여부.</description>
                      </property>
                      <property name="axisEnabled">
                        <type>boolean</type>
                        <description>해당 축의 사용 가능 여부.</description>
                      </property>
                      <property name="interlockEnabled">
                        <type>boolean</type>
                        <description>해당 축의 인터락 상태 여부.</description>
                      </property>
                      <property name="constantSurfaceSpeedControlEnabled">
                        <type>boolean</type>
                        <description>주속 일정 제어(CSS) 활성화 여부.</description>
                      </property>
                      <property name="axisCurrent">
                        <type>number</type>
                        <description>해당 축의 전류 정보.</description>
                      </property>
                      <property name="machineOrigin">
                        <type>number</type>
                        <description>기계 원점 좌표값.</description>
                      </property>
                      <property name="axisTemperature">
                        <type>number</type>
                        <description>해당 축의 온도 정보.</description>
                      </property>
                      <property name="axisPower">
                        <type>object</type>
                        <description>축의 전력 소비량 정보.</description>
                        <properties>
                          <property name="actualPowerConsumption">
                            <type>number</type>
                            <description>실 소비 전력의 적산값 (소비전력 - 회생전력).</description>
                          </property>
                          <property name="powerConsumption">
                            <type>number</type>
                            <description>소비 전력의 적산값.</description>
                          </property>
                          <property name="regeneratedPower">
                            <type>number</type>
                            <description>회생 전력의 적산값.</description>
                          </property>
                        </properties>
                      </property>
                    </properties>
                  </items>
                </property>
                <property name="spindle">
                  <type>array</type>
                  <description>스핀들 별 상태 정보 리스트. {spindle=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="spindleLoad">
                        <type>number</type>
                        <description>스핀들에 걸리는 부하.</description>
                      </property>
                      <property name="spindleOverride">
                        <type>number</type>
                        <description>스핀들 속도 오버라이드 비율.</description>
                      </property>
                      <property name="spindleLimit">
                        <type>number</type>
                        <description>최대 회전 속도 한계값.</description>
                      </property>
                      <property name="spindleEnabled">
                        <type>boolean</type>
                        <description>해당 스핀들의 사용 가능 여부.</description>
                      </property>
                      <property name="spindleCurrent">
                        <type>number</type>
                        <description>해당 스핀들의 전류 정보.</description>
                      </property>
                      <property name="spindleTemperature">
                        <type>number</type>
                        <description>해당 스핀들의 온도 정보.</description>
                      </property>
                      <property name="rpm">
                        <type>object</type>
                        <description>스핀들 회전 속도(RPM) 정보.</description>
                        <properties>
                          <property name="commandedSpeed">
                            <type>number</type>
                            <description>지령된 스핀들 회전 속도.</description>
                          </property>
                          <property name="actualSpeed">
                            <type>number</type>
                            <description>실제 측정된 스핀들 회전 속도.</description>
                          </property>
                          <property name="speedUnit">
                            <type>integer</type>
                            <description>속도 단위 (2: rpm, 3: mm/rev 등).</description>
                          </property>
                        </properties>
                      </property>
                      <property name="spindlePower">
                        <type>object</type>
                        <description>스핀들의 전력 소비량 정보.</description>
                        <properties>
                          <property name="actualPowerConsumption">
                            <type>number</type>
                            <description>실 소비 전력의 적산값.</description>
                          </property>
                          <property name="powerConsumption">
                            <type>number</type>
                            <description>소비 전력의 적산값.</description>
                          </property>
                          <property name="regeneratedPower">
                            <type>number</type>
                            <description>회생 전력의 적산값.</description>
                          </property>
                        </properties>
                      </property>
                    </properties>
                  </items>
                </property>
                <property name="feed">
                  <type>object</type>
                  <description>축 이송 관련 정보.</description>
                  <properties>
                    <property name="feedOverride">
                      <type>number</type>
                      <description>가공 이송 속도 오버라이드 비율.</description>
                    </property>
                    <property name="rapidOverride">
                      <type>number</type>
                      <description>급속 이송 속도 오버라이드 비율.</description>
                    </property>
                    <property name="feedRate">
                      <type>object</type>
                      <description>이송 속도(Feedrate) 정보.</description>
                      <properties>
                        <property name="commandedSpeed">
                          <type>number</type>
                          <description>지령된 이송 속도.</description>
                        </property>
                        <property name="actualSpeed">
                          <type>number</type>
                          <description>실제 측정된 이송 속도.</description>
                        </property>
                        <property name="speedUnit">
                          <type>integer</type>
                          <description>속도 단위 (0: mm/min, 1: inch/min 등).</description>
                        </property>
                      </properties>
                    </property>
                  </properties>
                </property>
                <property name="workStatus">
                  <type>array</type>
                  <description>가공 작업의 진척 상태 정보 리스트. {workStatus=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="workCounter">
                        <type>object</type>
                        <description>가공 수량 정보.</description>
                        <properties>
                          <property name="currentWorkCounter">
                            <type>integer</type>
                            <description>현재까지 가공한 수량.</description>
                          </property>
                          <property name="targetWorkCounter">
                            <type>integer</type>
                            <description>목표 가공 수량.</description>
                          </property>
                          <property name="totalWorkCounter">
                            <type>integer</type>
                            <description>총 가공 수량.</description>
                          </property>
                        </properties>
                      </property>
                      <property name="machiningTime">
                        <type>object</type>
                        <description>가공 시간 정보.</description>
                        <properties>
                          <property name="processingMachiningTime">
                            <type>number</type>
                            <description>현재 가공이 진행된 시간 (단위: 초).</description>
                          </property>
                          <property name="estimatedMachiningTime">
                            <type>number</type>
                            <description>예상 남은 가공 완료 시간 (SIEMENS 전용).</description>
                          </property>
                          <property name="machineOperationTime">
                            <type>number</type>
                            <description>자동 운전 모드에서의 총 운전 시간 (단위: 초).</description>
                          </property>
                          <property name="actualCuttingTime">
                            <type>number</type>
                            <description>실제 총 절삭 시간 (단위: 초).</description>
                          </property>
                        </properties>
                      </property>
                    </properties>
                  </items>
                </property>
                <property name="activeTool">
                  <type>object</type>
                  <description>현재 채널에서 활성화(사용 중인)된 공구 정보.</description>
                  <properties>
                    <property name="locationNumber">
                      <type>integer</type>
                      <description>공구가 매거진에 탑재된 위치 번호.</description>
                    </property>
                    <property name="toolName">
                      <type>string</type>
                      <description>공구 이름.</description>
                    </property>
                    <property name="toolNumber">
                      <type>integer</type>
                      <description>공구 식별 번호 (T 코드).</description>
                    </property>
                    <property name="numberOfEdges">
                      <type>integer</type>
                      <description>공구 날의 총 개수.</description>
                    </property>
                    <property name="toolEnabled">
                      <type>integer</type>
                      <description>공구 영역 등록 및 매거진 탑재 여부.</description>
                    </property>
                    <property name="magazineNumber">
                      <type>integer</type>
                      <description>공구가 탑재된 매거진 번호.</description>
                    </property>
                    <property name="sisterToolNumber">
                      <type>integer</type>
                      <description>할당된 대체 공구 번호.</description>
                    </property>
                    <property name="toolLifeUnit">
                      <type>integer</type>
                      <description>공구 수명 측정 단위 기준.</description>
                    </property>
                    <property name="toolGroupNumber">
                      <type>integer</type>
                      <description>공구가 참조된 공구 그룹 번호 리스트.</description>
                    </property>
                    <property name="toolUseOrderNumber">
                      <type>integer</type>
                      <description>그룹 내 공구 사용 순서 (FANUC 전용).</description>
                    </property>
                    <property name="toolStatus">
                      <type>integer</type>
                      <description>공구의 사용 상태.</description>
                    </property>
                    <property name="toolEdge">
                      <type>array</type>
                      <description>활성화된 공구의 날(edge) 정보 리스트. </description>
                      <items>
                        <type>object</type>
                        <properties>
                          <property name="edgeNumber">
                            <type>integer</type>
                            <description>공구 날 식별 번호.</description>
                          </property>
                          <property name="toolType">
                            <type>integer</type>
                            <description>공구 유형.</description>
                          </property>
                          <property name="lengthOffsetNumber">
                            <type>integer</type>
                            <description>공구 길이 보정 식별 번호.</description>
                          </property>
                          <property name="geoLengthOffset">
                            <type>number</type>
                            <description>공구 길이 X 보정값.</description>
                          </property>
                          <property name="wearLengthOffset">
                            <type>number</type>
                            <description>공구 길이 X 마모 보정값.</description>
                          </property>
                          <property name="radiusOffsetNumber">
                            <type>integer</type>
                            <description>공구 반경 보정 식별 번호.</description>
                          </property>
                          <property name="geoRadiusOffset">
                            <type>number</type>
                            <description>공구 반경 보정값.</description>
                          </property>
                          <property name="wearRadiusOffset">
                            <type>number</type>
                            <description>공구 반경 마모 보정값.</description>
                          </property>
                          <property name="edgeEnabled">
                            <type>boolean</type>
                            <description>공구 날 사용 가능 여부.</description>
                          </property>
                          <property name="geoLengthOffsetZ">
                            <type>number</type>
                            <description>공구 길이 Z 보정값.</description>
                          </property>
                          <property name="wearLengthOffsetZ">
                            <type>number</type>
                            <description>공구 길이 Z 마모 보정값.</description>
                          </property>
                          <property name="geoLengthOffsetY">
                            <type>number</type>
                            <description>공구 길이 Y 보정값.</description>
                          </property>
                          <property name="wearLengthOffsetY">
                            <type>number</type>
                            <description>공구 길이 Y 마모 보정값.</description>
                          </property>
                          <property name="geoOffsetNumber">
                            <type>integer</type>
                            <description>길이 X,Z, 반경의 식별 번호.</description>
                          </property>
                          <property name="wearOffsetNumber">
                            <type>integer</type>
                            <description>길이 X,Z, 반경 마모값의 식별 번호.</description>
                          </property>
                          <property name="cuttingEdgePosition">
                            <type>integer</type>
                            <description>공구 인선 방향.</description>
                          </property>
                          <property name="tipAngle">
                            <type>number</type>
                            <description>공구의 팁 각도.</description>
                          </property>
                          <property name="holderAngle">
                            <type>number</type>
                            <description>공구 홀더 각도.</description>
                          </property>
                          <property name="insertAngle">
                            <type>number</type>
                            <description>공구 인서트 각도.</description>
                          </property>
                          <property name="insertWidth">
                            <type>number</type>
                            <description>인선 너비 (SIEMENS 전용).</description>
                          </property>
                          <property name="insertLength">
                            <type>number</type>
                            <description>인선 길이 (SIEMENS 전용).</description>
                          </property>
                          <property name="referenceDirectionHolderAngle">
                            <type>number</type>
                            <description>홀더 각도 참조 방향 (SIEMENS 전용).</description>
                          </property>
                          <property name="directionOfSpindleRotation">
                            <type>integer</type>
                            <description>스핀들 회전 방향 (SIEMENS 전용).</description>
                          </property>
                          <property name="numberOfTeeth">
                            <type>integer</type>
                            <description>공구 날 개수 (SIEMENS 전용).</description>
                          </property>
                          <property name="toolLife">
                            <type>object</type>
                            <description>공구 수명 정보.</description>
                            <properties>
                              <property name="maxToolLife">
                                <type>number</type>
                                <description>최대 공구 수명.</description>
                              </property>
                              <property name="restToolLife">
                                <type>number</type>
                                <description>잔여 공구 수명.</description>
                              </property>
                              <property name="toolLifeCount">
                                <type>number</type>
                                <description>현재 공구 사용량.</description>
                              </property>
                              <property name="toolLifeAlarm">
                                <type>number</type>
                                <description>공구 수명 도달 경고 설정값 (SIEMENS 전용).</description>
                              </property>
                            </properties>
                          </property>
                        </properties>
                      </items>
                    </property>
                  </properties>
                </property>
                <property name="currentProgram">
                  <type>object</type>
                  <description>현재 실행 중인 NC 프로그램의 상태 정보.</description>
                  <properties>
                    <property name="sequenceNumber">
                      <type>integer</type>
                      <description>현재 실행 중인 시퀀스 번호(N 코드).</description>
                    </property>
                    <property name="currentBlockCounter">
                      <type>integer</type>
                      <description>실행 중인 블록 카운터.</description>
                    </property>
                    <property name="lastBlock">
                      <type>string</type>
                      <description>이전 블록 정보.</description>
                    </property>
                    <property name="currentBlock">
                      <type>string</type>
                      <description>현재 실행 중인 프로그램 블록 내용.</description>
                    </property>
                    <property name="nextBlock">
                      <type>string</type>
                      <description>다음 블록 정보.</description>
                    </property>
                    <property name="activePartProgram">
                      <type>string</type>
                      <description>실행 중인 프로그램 블록 정보(최대 200자).</description>
                    </property>
                    <property name="programMode">
                      <type>integer</type>
                      <description>프로그램 실행 모드 (0: Reset, 3: Start 등).</description>
                    </property>
                    <property name="currentWorkOffsetIndex">
                      <type>integer</type>
                      <description>현재 공작물 좌표계의 G 코드 인덱스.</description>
                    </property>
                    <property name="currentWorkOffsetCode">
                      <type>string</type>
                      <description>현재 공작물 좌표계의 G 코드 문자열.</description>
                    </property>
                    <property name="currentDepthLevel">
                      <type>integer</type>
                      <description>현재 프로그램의 레벨 (메인, 서브루틴 등).</description>
                    </property>
                    <property name="modal">
                      <type>array</type>
                      <description>G 코드 모달 정보 리스트. {modal=k}</description>
                      <items>
                        <type>object</type>
                        <properties>
                          <property name="modalIndex">
                            <type>integer</type>
                            <description>G 코드 인덱스.</description>
                          </property>
                          <property name="modalCode">
                            <type>string</type>
                            <description>G 코드 문자열.</description>
                          </property>
                        </properties>
                      </items>
                    </property>
                    <property name="overallBlock">
                      <type>array</type>
                      <description>실행 중인 블록 정보 리스트 (SIEMENS 전용). {overallBlock=k}</description>
                      <items>
                        <type>object</type>
                        <properties>
                          <property name="blockCounter">
                            <type>integer</type>
                            <description>블록 카운터.</description>
                          </property>
                          <property name="programName">
                            <type>string</type>
                            <description>프로그램 이름.</description>
                          </property>
                        </properties>
                      </items>
                    </property>
                    <property name="interruptBlock">
                      <type>array</type>
                      <description>프로그램 중단점 블록 정보 리스트 (SIEMENS 전용). {interruptBlock=k}</description>
                      <items>
                        <type>object</type>
                        <properties>
                          <property name="depthLevel">
                            <type>integer</type>
                            <description>중단점 블록의 프로그램 레벨.</description>
                          </property>
                          <property name="blockCounter">
                            <type>integer</type>
                            <description>중단점 블록의 카운터.</description>
                          </property>
                          <property name="programName">
                            <type>string</type>
                            <description>중단점 블록의 프로그램 이름.</description>
                          </property>
                          <property name="blockData">
                            <type>string</type>
                            <description>중단점 블록 데이터.</description>
                          </property>
                          <property name="searchType">
                            <type>integer</type>
                            <description>중단점 검색 유형.</description>
                          </property>
                          <property name="mainProgramName">
                            <type>string</type>
                            <description>중단점의 메인 프로그램 이름.</description>
                          </property>
                        </properties>
                      </items>
                    </property>
                    <property name="currentTotalWorkOffset">
                      <type>object</type>
                      <description>공작물 좌표계의 총 오프셋 정보.</description>
                      <properties>
                        <property name="workOffsetIndex">
                          <type>integer</type>
                          <description>G 코드 인덱스.</description>
                        </property>
                        <property name="workOffsetValue">
                          <type>array</type>
                          <description>축별 총 오프셋 값. {workOffsetValue=k}</description>
                          <items>
                            <type>number</type>
                          </items>
                        </property>
                        <property name="workOffsetRotation">
                          <type>array</type>
                          <description>축별 총 회전 오프셋 값. {workOffsetRotation=k}</description>
                          <items>
                            <type>number</type>
                          </items>
                        </property>
                        <property name="workOffsetScalingFactor">
                          <type>array</type>
                          <description>축별 총 스케일링 값. {workOffsetScalingFactor=k}</description>
                          <items>
                            <type>number</type>
                          </items>
                        </property>
                        <property name="workOffsetMirroringEnabled">
                          <type>array</type>
                          <description>축별 미러링 활성화 여부. {workOffsetMirroringEnabled=k}</description>
                          <items>
                            <type>boolean</type>
                          </items>
                        </property>
                      </properties>
                    </property>
                    <property name="currentFile">
                      <type>object</type>
                      <description>현재 실행 중인 프로그램 파일 정보.</description>
                      <properties>
                        <property name="programName">
                          <type>string</type>
                          <description>파일명.</description>
                        </property>
                        <property name="programPath">
                          <type>string</type>
                          <description>파일 경로.</description>
                        </property>
                        <property name="programSize">
                          <type>number</type>
                          <description>파일 크기 (byte).</description>
                        </property>
                        <property name="programDate">
                          <type>string</type>
                          <description>파일 생성 날짜.</description>
                        </property>
                        <property name="programNameWithPath">
                          <type>string</type>
                          <description>경로를 포함한 전체 파일명.</description>
                        </property>
                      </properties>
                    </property>
                    <property name="mainFile">
                      <type>object</type>
                      <description>현재 선택된(실행 중이 아닐 수 있는) 프로그램 파일 정보.</description>
                      <properties>
                        <property name="programName">
                          <type>string</type>
                          <description>파일명.</description>
                        </property>
                        <property name="programPath">
                          <type>string</type>
                          <description>파일 경로.</description>
                        </property>
                        <property name="programSize">
                          <type>number</type>
                          <description>파일 크기 (byte).</description>
                        </property>
                        <property name="programDate">
                          <type>string</type>
                          <description>파일 생성 날짜.</description>
                        </property>
                        <property name="programNameWithPath">
                          <type>string</type>
                          <description>경로를 포함한 전체 파일명.</description>
                        </property>
                      </properties>
                    </property>
                    <property name="controlOption">
                      <type>object</type>
                      <description>프로그램 실행 제어 옵션.</description>
                      <properties>
                        <property name="singleBlock">
                          <type>boolean</type>
                          <description>싱글 블록 실행 여부.</description>
                        </property>
                        <property name="dryRun">
                          <type>boolean</type>
                          <description>드라이 런 실행 여부.</description>
                        </property>
                        <property name="optionalStop">
                          <type>boolean</type>
                          <description>옵셔널 스톱(M01) 활성화 여부.</description>
                        </property>
                        <property name="blockSkip">
                          <type>array</type>
                          <description>블록 스킵 활성화 여부 리스트. {blockSkip=k}</description>
                          <items>
                            <type>boolean</type>
                          </items>
                        </property>
                        <property name="machineLock">
                          <type>boolean</type>
                          <description>머신 락 활성화 여부.</description>
                        </property>
                      </properties>
                    </property>
                  </properties>
                </property>
                <property name="workOffset">
                  <type>array</type>
                  <description>공작물 좌표계 오프셋 정보 리스트. {workOffset=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="workOffsetValue">
                        <type>array</type>
                        <description>축별 오프셋 값. {workOffsetValue=l}</description>
                        <items>
                          <type>number</type>
                        </items>
                      </property>
                      <property name="workOffsetRotation">
                        <type>array</type>
                        <description>축별 오프셋 회전량 (SIEMENS 전용). {workOffsetRotation=l}</description>
                        <items>
                          <type>number</type>
                        </items>
                      </property>
                      <property name="workOffsetScalingFactor">
                        <type>array</type>
                        <description>축별 오프셋 확장량 (SIEMENS 전용). {workOffsetScalingFactor=l}</description>
                        <items>
                          <type>number</type>
                        </items>
                      </property>
                      <property name="workOffsetMirroringEnabled">
                        <type>array</type>
                        <description>축별 미러링 활성화 여부 (SIEMENS 전용). {workOffsetMirroringEnabled=l}</description>
                        <items>
                          <type>boolean</type>
                        </items>
                      </property>
                      <property name="workOffsetFine">
                        <type>array</type>
                        <description>축별 오프셋 Fine 값 (SIEMENS 전용). {workOffsetFine=l}</description>
                        <items>
                          <type>number</type>
                        </items>
                      </property>
                    </properties>
                  </items>
                </property>
                <property name="alarm">
                  <type>array</type>
                  <description>발생한 알람 정보 리스트. {alarm=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="alarmText">
                        <type>string</type>
                        <description>알람 상세 내용.</description>
                      </property>
                      <property name="alarmCategory">
                        <type>string</type>
                        <description>알람 유형.</description>
                      </property>
                      <property name="alarmNumber">
                        <type>string</type>
                        <description>알람 번호.</description>
                      </property>
                      <property name="raisedTimeStamp">
                        <type>string</type>
                        <description>알람 발생 시각.</description>
                      </property>
                    </properties>
                  </items>
                </property>
                <property name="variable">
                  <type>array</type>
                  <description>사용자 변수(매크로 변수) 리스트. {variable=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="userVariable">
                        <type>number</type>
                        <description>사용자 변수 값.</description>
                      </property>
                    </properties>
                  </items>
                </property>
              </properties>
            </items>
          </property>
          <property name="pic">
            <type>object</type>
            <description>CNC 내부 PLC 메모리 데이터 모델.</description>
            <properties>
              <property name="memory">
                <type>object</type>
                <description>{machine=i}</description>
                <properties>
                  <property name="rbitBlock">
                    <type>array</type>
                    <description>읽기 전용 Bit 데이터 블록. {rbitBlock=j}</description>
                    <items>
                      <type>boolean</type>
                    </items>
                  </property>
                  <property name="bitBlock">
                    <type>array</type>
                    <description>읽기/쓰기 가능 Bit 데이터 블록. {bitBlock=j}</description>
                    <items>
                      <type>boolean</type>
                    </items>
                  </property>
                  <property name="rbyteBlock">
                    <type>array</type>
                    <description>읽기 전용 Byte 데이터 블록. {rbyteBlock=j}</description>
                    <items>
                      <type>integer</type>
                    </items>
                  </property>
                  <property name="byteBlock">
                    <type>array</type>
                    <description>읽기/쓰기 가능 Byte 데이터 블록. {byteBlock=j}</description>
                    <items>
                      <type>integer</type>
                    </items>
                  </property>
                  <property name="rwordBlock">
                    <type>array</type>
                    <description>읽기 전용 Word(2byte) 데이터 블록. {rwordBlock=j}</description>
                    <items>
                      <type>integer</type>
                    </items>
                  </property>
                  <property name="wordBlock">
                    <type>array</type>
                    <description>읽기/쓰기 가능 Word(2byte) 데이터 블록. {wordBlock=j}</description>
                    <items>
                      <type>integer</type>
                    </items>
                  </property>
                  <property name="rdwordBlock">
                    <type>array</type>
                    <description>읽기 전용 DWord(4byte) 데이터 블록. {rdwordBlock=j}</description>
                    <items>
                      <type>integer</type>
                    </items>
                  </property>
                  <property name="dwordBlock">
                    <type>array</type>
                    <description>읽기/쓰기 가능 DWord(4byte) 데이터 블록. {dwordBlock=j}</description>
                    <items>
                      <type>integer</type>
                    </items>
                  </property>
                  <property name="rqwordBlock">
                    <type>array</type>
                    <description>읽기 전용 QWord(8byte) 데이터 블록. {rqwordBlock=j}</description>
                    <items>
                      <type>integer</type>
                    </items>
                  </property>
                  <property name="qwordBlock">
                    <type>array</type>
                    <description>읽기/쓰기 가능 QWord(8byte) 데이터 블록. {qwordBlock=j}</description>
                    <items>
                      <type>integer</type>
                    </items>
                  </property>
                </properties>
              </property>
            </properties>
          </property>
          <property name="toolArea">
            <type>array</type>
            <description>공구 영역 정보 리스트. {toolArea=j}</description>
            <items>
              <type>object</type>
              <properties>
                <property name="toolAreaEnabled">
                  <type>boolean</type>
                  <description>해당 공구 영역 사용 가능 여부.</description>
                </property>
                <property name="numberOfMagazines">
                  <type>integer</type>
                  <description>사용 가능한 매거진 개수.</description>
                </property>
                <property name="numberOfRegisteredTools">
                  <type>integer</type>
                  <description>공구 영역에 등록된 총 공구 개수.</description>
                </property>
                <property name="numberOfLoadedTools">
                  <type>integer</type>
                  <description>매거진에 탑재된 총 공구 개수.</description>
                </property>
                <property name="numberOfToolGroups">
                  <type>integer</type>
                  <description>등록된 공구 그룹의 개수.</description>
                </property>
                <property name="numberOfToolOffsets">
                  <type>integer</type>
                  <description>등록된 공구 오프셋의 개수.</description>
                </property>
                <property name="magazine">
                  <type>array</type>
                  <description>매거진 정보 리스트. {magazine=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="magazineEnabled">
                        <type>boolean</type>
                        <description>해당 매거진 사용 가능 여부.</description>
                      </property>
                      <property name="magazineName">
                        <type>string</type>
                        <description>매거진 이름 (SIEMENS 전용).</description>
                      </property>
                      <property name="numberOfRealLocations">
                        <type>integer</type>
                        <description>매거진의 물리적 포트(위치) 개수.</description>
                      </property>
                      <property name="magazinePhysicalNumber">
                        <type>integer</type>
                        <description>매거진의 물리적 번호.</description>
                      </property>
                      <property name="numberOfLoadedTools">
                        <type>integer</type>
                        <description>해당 매거진에 탑재된 공구 개수.</description>
                      </property>
                    </properties>
                  </items>
                </property>
                <property name="tools">
                  <type>array</type>
                  <description>공구 번호 기준 공구 정보 리스트. {tools=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="locationNumber">
                        <type>integer</type>
                        <description>공구가 매거진에 탑재된 위치 번호.</description>
                      </property>
                      <property name="toolName">
                        <type>string</type>
                        <description>공구 이름.</description>
                      </property>
                      <property name="numberOfEdges">
                        <type>integer</type>
                        <description>공구 날의 총 개수.</description>
                      </property>
                      <property name="toolEnabled">
                        <type>integer</type>
                        <description>공구 영역 등록 및 매거진 탑재 여부.</description>
                      </property>
                      <property name="magazineNumber">
                        <type>integer</type>
                        <description>공구가 탑재된 매거진 번호.</description>
                      </property>
                      <property name="sisterToolNumber">
                        <type>integer</type>
                        <description>할당된 대체 공구 번호.</description>
                      </property>
                      <property name="toolLifeUnit">
                        <type>integer</type>
                        <description>공구 수명 측정 단위 기준.</description>
                      </property>
                      <property name="toolGroupNumber">
                        <type>array</type>
                        <description>공구가 참조된 공구 그룹 번호 리스트.</description>
                        <items>
                          <type>integer</type>
                        </items>
                      </property>
                      <property name="toolUseOrderNumber">
                        <type>integer</type>
                        <description>그룹 내 공구 사용 순서 (FANUC 전용).</description>
                      </property>
                      <property name="toolStatus">
                        <type>integer</type>
                        <description>공구의 사용 상태.</description>
                      </property>
                      <property name="toolEdge">
                        <type>array</type>
                        <description>공구 날 정보 리스트. {toolEdge=l}</description>
                        <items>
                          <type>object</type>
                          <properties>
                            <property name="toolType">
                              <type>integer</type>
                              <description>공구 유형.</description>
                            </property>
                            <property name="lengthOffsetNumber">
                              <type>integer</type>
                              <description>공구 길이 보정 식별 번호. {lengthOffsetNumber=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="geoLengthOffset">
                              <type>number</type>
                              <description>공구 길이 X 보정값.{geoLengthOffset=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearLengthOffset">
                              <type>number</type>
                              <description>공구 길이 X 마모 보정값.{wearLengthOffset=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="radiusOffsetNumber">
                              <type>integer</type>
                              <description>공구 반경 보정 식별 번호. {radiusOffsetNumber=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="geoRadiusOffset">
                              <type>number</type>
                              <description>공구 반경 보정값. {geoRadiusOffset=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearRadiusOffset">
                              <type>number</type>
                              <description>공구 반경 마모 보정값. {wearRadiusOffset=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="edgeEnabled">
                              <type>boolean</type>
                              <description>공구 날 사용 가능 여부.</description>
                            </property>
                            <property name="geoLengthOffsetZ">
                              <type>number</type>
                              <description>공구 길이 Z 보정값. {geoLengthOffsetZ=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearLengthOffsetZ">
                              <type>number</type>
                              <description>공구 길이 Z 마모 보정값.{wearLengthOffsetZ=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="geoLengthOffsetY">
                              <type>number</type>
                              <description>공구 길이 Y 보정값.{geoLengthOffsetY=m : m번째 공구 그룹} </description>
                            </property>
                            <property name="wearLengthOffsetY">
                              <type>number</type>
                              <description>공구 길이 Y 마모 보정값.{wearLengthOffsetY=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="geoOffsetNumber">
                              <type>integer</type>
                              <description>길이 X,Z, 반경의 식별 번호.{geoOffsetNumber=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearOffsetNumber">
                              <type>integer</type>
                              <description>길이 X,Z, 반경 마모값의 식별 번호.{wearOffsetNumber=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="cuttingEdgePosition">
                              <type>integer</type>
                              <description>공구 인선 방향.{cuttingEdgePosition=m : m번째 공구 그룹} </description>
                            </property>
                            <property name="tipAngle">
                              <type>number</type>
                              <description>공구의 팁 각도.</description>
                            </property>
                            <property name="holderAngle">
                              <type>number</type>
                              <description>공구 홀더 각도.</description>
                            </property>
                            <property name="insertAngle">
                              <type>number</type>
                              <description>공구 인서트 각도.</description>
                            </property>
                            <property name="insertWidth">
                              <type>number</type>
                              <description>인선 너비 (SIEMENS 전용).</description>
                            </property>
                            <property name="insertLength">
                              <type>number</type>
                              <description>인선 길이 (SIEMENS 전용).</description>
                            </property>
                            <property name="referenceDirectionHolderAngle">
                              <type>number</type>
                              <description>홀더 각도 참조 방향 (SIEMENS 전용).</description>
                            </property>
                            <property name="directionOfSpindleRotation">
                              <type>integer</type>
                              <description>스핀들 회전 방향 (SIEMENS 전용).</description>
                            </property>
                            <property name="numberOfTeeth">
                              <type>integer</type>
                              <description>공구 날 개수 (SIEMENS 전용).</description>
                            </property>
                            <property name="toolLife">
                              <type>object</type>
                              <description>공구 수명 정보 (읽기/쓰기 가능).</description>
                              <properties>
                                <property name="maxToolLife">
                                  <type>number</type>
                                  <description>최대 공구 수명.{maxToolLife = m : m번째 공구 그룹}</description>
                                </property>
                                <property name="restToolLife">
                                  <type>number</type>
                                  <description>잔여 공구 수명.{restToolLife = m : m번째 공구 그룹}</description>
                                </property>
                                <property name="toolLifeCount">
                                  <type>number</type>
                                  <description>현재 공구 사용량.{toolLifeCount = m : m번째 공구 그룹}</description>
                                </property>
                                <property name="toolLifeAlarm">
                                  <type>number</type>
                                  <description>공구 수명 도달 경고 설정값.</description>
                                </property>
                              </properties>
                            </property>
                          </properties>
                        </items>
                      </property>
                    </properties>
                  </items>
                </property>
                <property name="registerTools">
                  <type>array</type>
                  <description>등록 순서 기준 공구 정보 리스트. {registerTools=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="locationNumber">
                        <type>integer</type>
                        <description>공구가 매거진에 탑재된 위치 번호.</description>
                      </property>
                      <property name="toolName">
                        <type>string</type>
                        <description>공구 이름.</description>
                      </property>
                      <property name="numberOfEdges">
                        <type>integer</type>
                        <description>공구 날의 총 개수.</description>
                      </property>
                      <property name="toolEnabled">
                        <type>integer</type>
                        <description>공구 영역 등록 및 매거진 탑재 여부.</description>
                      </property>
                      <property name="magazineNumber">
                        <type>integer</type>
                        <description>공구가 탑재된 매거진 번호.</description>
                      </property>
                      <property name="sisterToolNumber">
                        <type>integer</type>
                        <description>할당된 대체 공구 번호.</description>
                      </property>
                      <property name="toolLifeUnit">
                        <type>integer</type>
                        <description>공구 수명 측정 단위 기준.</description>
                      </property>
                      <property name="toolGroupNumber">
                        <type>array</type>
                        <description>공구가 참조된 공구 그룹 번호 리스트.</description>
                        <items>
                          <type>integer</type>
                        </items>
                      </property>
                      <property name="toolUseOrderNumber">
                        <type>integer</type>
                        <description>그룹 내 공구 사용 순서 (FANUC 전용).</description>
                      </property>
                      <property name="toolStatus">
                        <type>integer</type>
                        <description>공구의 사용 상태.</description>
                      </property>
                      <property name="toolEdge">
                        <type>array</type>
                        <description>공구 날 정보 리스트. {toolEdge=l}</description>
                        <items>
                          <type>object</type>
                          <properties>
                            <property name="toolType">
                              <type>integer</type>
                              <description>공구 유형.</description>
                            </property>
                            <property name="lengthOffsetNumber">
                              <type>integer</type>
                              <description>공구 길이 보정 식별 번호.{lengthOffsetNumber=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="geoLengthOffset">
                              <type>number</type>
                              <description>공구 길이 X 보정값.{geoLengthOffset=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearLengthOffset">
                              <type>number</type>
                              <description>공구 길이 X 마모 보정값.{wearLengthOffset=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="radiusOffsetNumber">
                              <type>integer</type>
                              <description>공구 반경 보정 식별 번호.{radiusOffsetNumber=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="geoRadiusOffset">
                              <type>number</type>
                              <description>공구 반경 보정값.{geoRadiusOffset=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearRadiusOffset">
                              <type>number</type>
                              <description>공구 반경 마모 보정값.{wearRadiusOffset=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="edgeEnabled">
                              <type>boolean</type>
                              <description>공구 날 사용 가능 여부.</description>
                            </property>
                            <property name="geoLengthOffsetZ">
                              <type>number</type>
                              <description>공구 길이 Z 보정값.{geoLengthOffsetZ=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearLengthOffsetZ">
                              <type>number</type>
                              <description>공구 길이 Z 마모 보정값. {wearLengthOffsetZ=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="geoLengthOffsetY">
                              <type>number</type>
                              <description>공구 길이 Y 보정값.{geoLengthOffsetY=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearLengthOffsetY">
                              <type>number</type>
                              <description>공구 길이 Y 마모 보정값.{wearLengthOffsetY=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="geoOffsetNumber">
                              <type>integer</type>
                              <description>길이 X,Z, 반경의 식별 번호.{geoOffsetNumber=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="wearOffsetNumber">
                              <type>integer</type>
                              <description>길이 X,Z, 반경 마모값의 식별 번호.{wearOffsetNumber=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="cuttingEdgePosition">
                              <type>integer</type>
                              <description>공구 인선 방향.{cuttingEdgePosition=m : m번째 공구 그룹}</description>
                            </property>
                            <property name="tipAngle">
                              <type>number</type>
                              <description>공구의 팁 각도.</description>
                            </property>
                            <property name="holderAngle">
                              <type>number</type>
                              <description>공구 홀더 각도.</description>
                            </property>
                            <property name="insertAngle">
                              <type>number</type>
                              <description>공구 인서트 각도.</description>
                            </property>
                            <property name="insertWidth">
                              <type>number</type>
                              <description>인선 너비 (SIEMENS 전용).</description>
                            </property>
                            <property name="insertLength">
                              <type>number</type>
                              <description>인선 길이 (SIEMENS 전용).</description>
                            </property>
                            <property name="referenceDirectionHolderAngle">
                              <type>number</type>
                              <description>홀더 각도 참조 방향 (SIEMENS 전용).</description>
                            </property>
                            <property name="directionOfSpindleRotation">
                              <type>integer</type>
                              <description>스핀들 회전 방향 (SIEMENS 전용).</description>
                            </property>
                            <property name="numberOfTeeth">
                              <type>integer</type>
                              <description>공구 날 개수 (SIEMENS 전용).</description>
                            </property>
                            <property name="toolLife">
                              <type>object</type>
                              <description>공구 수명 정보 (읽기/쓰기 가능).</description>
                              <properties>
                                <property name="maxToolLife">
                                  <type>number</type>
                                  <description>최대 공구 수명.{maxToolLife = m : m번째 공구 그룹}</description>
                                </property>
                                <property name="restToolLife">
                                  <type>number</type>
                                  <description>잔여 공구 수명.{restToolLife = m : m번째 공구 그룹}</description>
                                </property>
                                <property name="toolLifeCount">
                                  <type>number</type>
                                  <description>현재 공구 사용량.{toolLifeCount = m : m번째 공구 그룹}</description>
                                </property>
                                <property name="toolLifeAlarm">
                                  <type>number</type>
                                  <description>공구 수명 도달 경고 설정값.</description>
                                </property>
                              </properties>
                            </property>
                          </properties>
                        </items>
                      </property>
                    </properties>
                  </items>
                </property>
              </properties>
            </items>
          </property>
          <property name="buffer">
            <type>array</type>
            <description>시계열 데이터 수집 버퍼 정보 리스트. {buffer=j}</description>
            <items>
              <type>object</type>
              <properties>
                <property name="bufferEnabled">
                  <type>boolean</type>
                  <description>해당 버퍼 사용 가능 여부.</description>
                </property>
                <property name="numberOfStream">
                  <type>integer</type>
                  <description>해당 버퍼의 최대 스트림 개수.</description>
                </property>
                <property name="statusOfStream">
                  <type>integer</type>
                  <description>스트림 상태 (0: 설정 가능, 3: 수집 중 등).</description>
                </property>
                <property name="modOfStream">
                  <type>integer</type>
                  <description>스트림 수집 모드 (0: 반복 수집, 1: 1회 수집).</description>
                </property>
                <property name="machineChannelOfStream">
                  <type>integer</type>
                  <description>스트림 수집 시 사용할 채널.</description>
                </property>
                <property name="periodOfStream">
                  <type>integer</type>
                  <description>1회 수집 기간 (단위: ms).</description>
                </property>
                <property name="triggerOfStream">
                  <type>integer</type>
                  <description>수집 시작 트리거 (0: 즉시, 1이상: 시퀀스 번호).</description>
                </property>
                <property name="frequencyOfStream">
                  <type>integer</type>
                  <description>모든 스트림에 공통으로 적용할 수집 주파수 (Hz).</description>
                </property>
                <property name="stream">
                  <type>array</type>
                  <description>개별 센서 데이터 스트림 채널 리스트. {stream=k}</description>
                  <items>
                    <type>object</type>
                    <properties>
                      <property name="streamEnabled">
                        <type>boolean</type>
                        <description>해당 스트림 사용 가능 여부.</description>
                      </property>
                      <property name="streamFrequency">
                        <type>integer</type>
                        <description>해당 스트림의 수집 주파수 (Hz).</description>
                      </property>
                      <property name="streamCategory">
                        <type>integer</type>
                        <description>수집 대상 데이터 카테고리.</description>
                      </property>
                      <property name="streamSubcategory">
                        <type>integer</type>
                        <description>수집 대상 데이터 서브카테고리 (축/스핀들 번호 등).</description>
                      </property>
                      <property name="streamType">
                        <type>integer</type>
                        <description>수집 유형 (KCNC 전용).</description>
                      </property>
                      <property name="streamStartBit">
                        <type>integer</type>
                        <description>수집 유형이 Bit일 때 Start Bit (KCNC 전용).</description>
                      </property>
                      <property name="streamEndBit">
                        <type>integer</type>
                        <description>수집 유형이 Bit일 때 End Bit (KCNC 전용).</description>
                      </property>
                      <property name="value">
                        <type>number</type>
                        <description>해당 스트림에서 마지막으로 수집된 데이터 값.</description>
                      </property>
                    </properties>
                  </items>
                </property>
              </properties>
            </items>
          </property>
        </properties>
      </items>
    </property>
  </properties>
</schema>