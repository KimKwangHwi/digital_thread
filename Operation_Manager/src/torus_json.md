
[URI 생성 예시]
장비 모델명 조회
data://machine/cncModel?machine=1

첫 번째 장비의 첫 번째 채널, 두 번째 축의 부하 조회
data://machine/channel/axis/axisLoad?machine=1&channel=1&axis=2

첫 번째 장비의 첫 번째 채널, 첫 번째 스핀들의 소비 전력 조회
data://machine/channel/spindle/spindlePower/powerConsumption?machine=1&channel=1&spindle=1



### 데이터 모델 계층 구조, 각 데이터 설명, 필요 파라미터


{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TORUS Platform Machine Data Model",
  "description": "TORUS Platform의 전체 데이터 모델에 대한 JSON 스키마입니다. 제공된 목록에 따라 특정 속성은 array 타입으로 정의되었습니다.",
  "type": "object",
  "properties": {
    "machine": {
      "type": "array",
      "description": "단위 공작기계의 리스트. 필터 `machine=i`를 사용하여 특정 장비를 식별합니다.",
      "items": {
        "type": "object",
        "properties": {
          "cncModel": {
            "type": "string",
            "description": "해당 장비에 탑재된 NC의 모델명."
          },
          "numberOfChannels": {
            "type": "integer",
            "description": "장비에서 사용 가능한 채널(계통)의 개수."
          },
          "cncVendor": {
            "type": "integer",
            "description": "NC 제조사 코드 (1: FANUC, 2: SIEMENS, 3: CSCAM, 4: MITSUBISHI, 5: KCNC)."
          },
          "ncLinkState": {
            "type": "boolean",
            "description": "NC와의 통신 연결 상태."
          },
          "currentAccessLevel": {
            "type": "integer",
            "description": "프로그램/디렉토리 접근에 대한 사용 권한 수준 (SIEMENS 전용, 1~7단계)."
          },
          "basicLengthUnit": {
            "type": "integer",
            "description": "장비가 사용하는 기본 길이 단위 (0: Metric, 1: Inches 등)."
          },
          "machinePowerOnTime": {
            "type": "number",
            "description": "장비의 전원이 켜진 시간 (단위: 분)."
          },
          "currentCncTime": {
            "type": "string",
            "format": "date-time",
            "description": "장비에 설정된 현재 시각 (형식: yyyy-MM-ddTHH:mm:ss)."
          },
          "machineType": {
            "type": "integer",
            "description": "장비의 타입 (1: Milling, 2: Lathe 등)."
          },
          "ncMemory": {
            "type": "object",
            "description": "NC 프로그램 저장 메모리 용량에 관한 정보를 포함합니다.",
            "properties": {
              "totalCapacity": {
                "type": "number",
                "description": "NC 메모리의 전체 용량 (단위: byte)."
              },
              "usedCapacity": {
                "type": "number",
                "description": "사용 중인 NC 메모리 용량 (단위: byte)."
              },
              "freeCapacity": {
                "type": "number",
                "description": "NC 메모리의 남은 용량 (단위: byte)."
              },
              "rootPath": {
                "type": "string",
                "description": "NC 메모리의 기본(루트) 경로."
              }
            }
          },
          "channel": {
            "type": "array",
            "description": "채널 별 상태 정보 리스트. {channel=j}",
            "items": {
              "type": "object",
              "properties": {
                "channelEnabled": {
                  "type": "boolean",
                  "description": "해당 채널의 활성화 여부."
                },
                "toolAreaNumber": {
                  "type": "integer",
                  "description": "해당 채널에서 사용 가능한 공구 영역의 식별 번호."
                },
                "numberOfAxes": {
                  "type": "integer",
                  "description": "해당 채널에서 사용 가능한 축의 개수."
                },
                "numberOfSpindles": {
                  "type": "integer",
                  "description": "해당 채널에서 사용 가능한 스핀들의 개수."
                },
                "alarmStatus": {
                  "type": "integer",
                  "description": "채널의 알람 상태 (0: No alarm, 1: Alarm 등)."
                },
                "numberOfAlarms": {
                  "type": "integer",
                  "description": "해당 채널에서 발생한 알람의 총 개수."
                },
                "operateMode": {
                  "type": "integer",
                  "description": "공작기계의 운전 모드 (0: JOG, 1: MDI, 2: MEMORY 등)."
                },
                "numberOfWorkOffsets": {
                  "type": "integer",
                  "description": "사용 가능한 공작물 좌표계의 개수."
                },
                "ncState": {
                  "type": "integer",
                  "description": "CNC의 작동 상태 (0: Reset, 1: Stop, 2: Hold, 3: Start 등)."
                },
                "motionStatus": {
                  "type": "integer",
                  "description": "장비의 현재 모션 상태 (1: Motion, 2: Dwell 등)."
                },
                "emergencyStatus": {
                  "type": "integer",
                  "description": "비상 정지(Emergency) 상태 여부 (0: Not emergency, 1: Emergency)."
                },
                "axis": {
                  "type": "array",
                  "description": "축 별 상태 정보 리스트. {axis=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                      "machinePosition": {
                        "type": "number",
                        "description": "기계 좌표계 기준 현재 위치."
                      },
                      "workPosition": {
                        "type": "number",
                        "description": "공작물 좌표계 기준 현재 위치."
                      },
                      "distanceToGo": {
                        "type": "number",
                        "description": "지령 위치까지 남은 이동 거리."
                      },
                      "relativePosition": {
                        "type": "number",
                        "description": "상대 좌표계 기준 현재 위치."
                      },
                      "axisName": {
                        "type": "string",
                        "description": "절대 좌표계의 축 이름."
                      },
                      "relativeAxisName": {
                        "type": "string",
                        "description": "상대 좌표계의 축 이름 (FANUC 전용)."
                      },
                      "axisLoad": {
                        "type": "number",
                        "description": "축에 걸리는 부하."
                      },
                      "axisFeed": {
                        "type": "number",
                        "description": "현재 축의 이송 속도."
                      },
                      "axisLimitPlus": {
                        "type": "number",
                        "description": "'+' 방향 최대 이동 한계값."
                      },
                      "axisLimitMinus": {
                        "type": "number",
                        "description": "'-' 방향 최대 이동 한계값."
                      },
                      "workAreaLimitPlus": {
                        "type": "number",
                        "description": "작업 금지 영역 '+' 방향 한계값."
                      },
                      "workAreaLimitMinus": {
                        "type": "number",
                        "description": "작업 금지 영역 '-' 방향 한계값."
                      },
                      "workAreaLimitPlusEnabled": {
                        "type": "boolean",
                        "description": "작업 금지 영역 '+' 방향 활성화 여부."
                      },
                      "workAreaLimitMinusEnabled": {
                        "type": "boolean",
                        "description": "작업 금지 영역 '-' 방향 활성화 여부."
                      },
                      "axisEnabled": {
                        "type": "boolean",
                        "description": "해당 축의 사용 가능 여부."
                      },
                      "interlockEnabled": {
                        "type": "boolean",
                        "description": "해당 축의 인터락 상태 여부."
                      },
                      "constantSurfaceSpeedControlEnabled": {
                        "type": "boolean",
                        "description": "주속 일정 제어(CSS) 활성화 여부."
                      },
                      "axisCurrent": {
                        "type": "number",
                        "description": "해당 축의 전류 정보."
                      },
                      "machineOrigin": {
                        "type": "number",
                        "description": "기계 원점 좌표값."
                      },
                      "axisTemperature": {
                        "type": "number",
                        "description": "해당 축의 온도 정보."
                      },
                      "axisPower": {
                        "type": "object",
                        "description": "축의 전력 소비량 정보.",
                        "properties": {
                          "actualPowerConsumption": {
                            "type": "number",
                            "description": "실 소비 전력의 적산값 (소비전력 - 회생전력)."
                          },
                          "powerConsumption": {
                            "type": "number",
                            "description": "소비 전력의 적산값."
                          },
                          "regeneratedPower": {
                            "type": "number",
                            "description": "회생 전력의 적산값."
                          }
                        }
                      }
                    }
                  }
                },
                "spindle": {
                  "type": "array",
                  "description": "스핀들 별 상태 정보 리스트. {spindle=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                      "spindleLoad": {
                        "type": "number",
                        "description": "스핀들에 걸리는 부하."
                      },
                      "spindleOverride": {
                        "type": "number",
                        "description": "스핀들 속도 오버라이드 비율."
                      },
                      "spindleLimit": {
                        "type": "number",
                        "description": "최대 회전 속도 한계값."
                      },
                      "spindleEnabled": {
                        "type": "boolean",
                        "description": "해당 스핀들의 사용 가능 여부."
                      },
                      "spindleCurrent": {
                        "type": "number",
                        "description": "해당 스핀들의 전류 정보."
                      },
                      "spindleTemperature": {
                        "type": "number",
                        "description": "해당 스핀들의 온도 정보."
                      },
                      "rpm": {
                        "type": "object",
                        "description": "스핀들 회전 속도(RPM) 정보.",
                        "properties": {
                          "commandedSpeed": {
                            "type": "number",
                            "description": "지령된 스핀들 회전 속도."
                          },
                          "actualSpeed": {
                            "type": "number",
                            "description": "실제 측정된 스핀들 회전 속도."
                          },
                          "speedUnit": {
                            "type": "integer",
                            "description": "속도 단위 (2: rpm, 3: mm/rev 등)."
                          }
                        }
                      },
                      "spindlePower": {
                        "type": "object",
                        "description": "스핀들의 전력 소비량 정보.",
                        "properties": {
                          "actualPowerConsumption": {
                            "type": "number",
                            "description": "실 소비 전력의 적산값."
                          },
                          "powerConsumption": {
                            "type": "number",
                            "description": "소비 전력의 적산값."
                          },
                          "regeneratedPower": {
                            "type": "number",
                            "description": "회생 전력의 적산값."
                          }
                        }
                      }
                    }
                  }
                },
                "feed": {
                  "type": "object",
                  "description": "축 이송 관련 정보.",
                  "properties": {
                    "feedOverride": {
                      "type": "number",
                      "description": "가공 이송 속도 오버라이드 비율."
                    },
                    "rapidOverride": {
                      "type": "number",
                      "description": "급속 이송 속도 오버라이드 비율."
                    },
                    "feedRate": {
                      "type": "object",
                      "description": "이송 속도(Feedrate) 정보.",
                      "properties": {
                        "commandedSpeed": {
                          "type": "number",
                          "description": "지령된 이송 속도."
                        },
                        "actualSpeed": {
                          "type": "number",
                          "description": "실제 측정된 이송 속도."
                        },
                        "speedUnit": {
                          "type": "integer",
                          "description": "속도 단위 (0: mm/min, 1: inch/min 등)."
                        }
                      }
                    }
                  }
                },
                "workStatus": {
                  "type": "array",
                  "description": "가공 작업의 진척 상태 정보 리스트. {workStatus=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                      "workCounter": {
                        "type": "object",
                        "description": "가공 수량 정보.",
                        "properties": {
                          "currentWorkCounter": {
                            "type": "integer",
                            "description": "현재까지 가공한 수량."
                          },
                          "targetWorkCounter": {
                            "type": "integer",
                            "description": "목표 가공 수량."
                          },
                          "totalWorkCounter": {
                            "type": "integer",
                            "description": "총 가공 수량."
                          }
                        }
                      },
                      "machiningTime": {
                        "type": "object",
                        "description": "가공 시간 정보.",
                        "properties": {
                          "processingMachiningTime": {
                            "type": "number",
                            "description": "현재 가공이 진행된 시간 (단위: 초)."
                          },
                          "estimatedMachiningTime": {
                            "type": "number",
                            "description": "예상 남은 가공 완료 시간 (SIEMENS 전용)."
                          },
                          "machineOperationTime": {
                            "type": "number",
                            "description": "자동 운전 모드에서의 총 운전 시간 (단위: 초)."
                          },
                          "actualCuttingTime": {
                            "type": "number",
                            "description": "실제 총 절삭 시간 (단위: 초)."
                          }
                        }
                      }
                    }
                  }
                },
                "activeTool": {
                  "type": "object",
                  "description": "현재 채널에서 활성화(사용 중인)된 공구 정보.",
                  "properties": {
                    "locationNumber": { "type": "integer", "description": "공구가 매거진에 탑재된 위치 번호." },
                    "toolName": { "type": "string", "description": "공구 이름." },
                    "toolNumber": { "type": "integer", "description": "공구 식별 번호 (T 코드)." },
                    "numberOfEdges": { "type": "integer", "description": "공구 날의 총 개수." },
                    "toolEnabled": { "type": "integer", "description": "공구 영역 등록 및 매거진 탑재 여부." },
                    "magazineNumber": { "type": "integer", "description": "공구가 탑재된 매거진 번호." },
                    "sisterToolNumber": { "type": "integer", "description": "할당된 대체 공구 번호." },
                    "toolLifeUnit": { "type": "integer", "description": "공구 수명 측정 단위 기준." },
                    "toolGroupNumber": { "type": "integer", "description": "공구가 참조된 공구 그룹 번호 리스트." },
                    "toolUseOrderNumber": { "type": "integer", "description": "그룹 내 공구 사용 순서 (FANUC 전용)." },
                    "toolStatus": { "type": "integer", "description": "공구의 사용 상태." },
                    "toolEdge": {
                      "type": "array",
                      "description": "활성화된 공구의 날(edge) 정보 리스트.",
                      "items": {
                        "type": "object",
                        "properties": {
                           "edgeNumber": { "type": "integer", "description": "공구 날 식별 번호." },
                           "toolType": { "type": "integer", "description": "공구 유형." },
                           "lengthOffsetNumber": { "type": "integer", "description": "공구 길이 보정 식별 번호." },
                           "geoLengthOffset": { "type": "number", "description": "공구 길이 X 보정값." },
                           "wearLengthOffset": { "type": "number", "description": "공구 길이 X 마모 보정값." },
                           "radiusOffsetNumber": { "type": "integer", "description": "공구 반경 보정 식별 번호." },
                           "geoRadiusOffset": { "type": "number", "description": "공구 반경 보정값." },
                           "wearRadiusOffset": { "type": "number", "description": "공구 반경 마모 보정값." },
                           "edgeEnabled": { "type": "boolean", "description": "공구 날 사용 가능 여부." },
                           "geoLengthOffsetZ": { "type": "number", "description": "공구 길이 Z 보정값." },
                           "wearLengthOffsetZ": { "type": "number", "description": "공구 길이 Z 마모 보정값." },
                           "geoLengthOffsetY": { "type": "number", "description": "공구 길이 Y 보정값." },
                           "wearLengthOffsetY": { "type": "number", "description": "공구 길이 Y 마모 보정값." },
                           "geoOffsetNumber": { "type": "integer", "description": "길이 X,Z, 반경의 식별 번호." },
                           "wearOffsetNumber": { "type": "integer", "description": "길이 X,Z, 반경 마모값의 식별 번호." },
                           "cuttingEdgePosition": { "type": "integer", "description": "공구 인선 방향." },
                           "tipAngle": { "type": "number", "description": "공구의 팁 각도." },
                           "holderAngle": { "type": "number", "description": "공구 홀더 각도." },
                           "insertAngle": { "type": "number", "description": "공구 인서트 각도." },
                           "insertWidth": { "type": "number", "description": "인선 너비 (SIEMENS 전용)." },
                           "insertLength": { "type": "number", "description": "인선 길이 (SIEMENS 전용)." },
                           "referenceDirectionHolderAngle": { "type": "number", "description": "홀더 각도 참조 방향 (SIEMENS 전용)." },
                           "directionOfSpindleRotation": { "type": "integer", "description": "스핀들 회전 방향 (SIEMENS 전용)." },
                           "numberOfTeeth": { "type": "integer", "description": "공구 날 개수 (SIEMENS 전용)." },
                          "toolLife": {
                            "type": "object",
                            "description": "공구 수명 정보.",
                            "properties": {
                              "maxToolLife": { "type": "number", "description": "최대 공구 수명." },
                              "restToolLife": { "type": "number", "description": "잔여 공구 수명." },
                              "toolLifeCount": { "type": "number", "description": "현재 공구 사용량." },
                              "toolLifeAlarm": { "type": "number", "description": "공구 수명 도달 경고 설정값 (SIEMENS 전용)." }
                            }
                          }
                        }
                      }
                    }
                  }
                },
                "currentProgram": {
                  "type": "object",
                  "description": "현재 실행 중인 NC 프로그램의 상태 정보.",
                  "properties": {
                    "sequenceNumber": { "type": "integer", "description": "현재 실행 중인 시퀀스 번호(N 코드)." },
                    "currentBlockCounter": { "type": "integer", "description": "실행 중인 블록 카운터." },
                    "lastBlock": { "type": "string", "description": "이전 블록 정보." },
                    "currentBlock": { "type": "string", "description": "현재 실행 중인 프로그램 블록 내용." },
                    "nextBlock": { "type": "string", "description": "다음 블록 정보." },
                    "activePartProgram": { "type": "string", "description": "실행 중인 프로그램 블록 정보(최대 200자)." },
                    "programMode": { "type": "integer", "description": "프로그램 실행 모드 (0: Reset, 3: Start 등)." },
                    "currentWorkOffsetIndex": { "type": "integer", "description": "현재 공작물 좌표계의 G 코드 인덱스." },
                    "currentWorkOffsetCode": { "type": "string", "description": "현재 공작물 좌표계의 G 코드 문자열." },
                    "currentDepthLevel": { "type": "integer", "description": "현재 프로그램의 레벨 (메인, 서브루틴 등)." },
                    "modal": {
                      "type": "array",
                      "description": "G 코드 모달 정보 리스트. {modal=k}",
                      "items": {
                        "type": "object",
                        "properties": {
                          "modalIndex": { "type": "integer", "description": "G 코드 인덱스." },
                          "modalCode": { "type": "string", "description": "G 코드 문자열." }
                        }
                      }
                    },
                    "overallBlock": {
                      "type": "array",
                      "description": "실행 중인 블록 정보 리스트 (SIEMENS 전용). {overallBlock=k}",
                      "items": {
                        "type": "object",
                        "properties": {
                          "blockCounter": { "type": "integer", "description": "블록 카운터." },
                          "programName": { "type": "string", "description": "프로그램 이름." }
                        }
                      }
                    },
                    "interruptBlock": {
                      "type": "array",
                      "description": "프로그램 중단점 블록 정보 리스트 (SIEMENS 전용). {interruptBlock=k}",
                      "items": {
                        "type": "object",
                        "properties": {
                          "depthLevel": { "type": "integer", "description": "중단점 블록의 프로그램 레벨." },
                          "blockCounter": { "type": "integer", "description": "중단점 블록의 카운터." },
                          "programName": { "type": "string", "description": "중단점 블록의 프로그램 이름." },
                          "blockData": { "type": "string", "description": "중단점 블록 데이터." },
                          "searchType": { "type": "integer", "description": "중단점 검색 유형." },
                          "mainProgramName": { "type": "string", "description": "중단점의 메인 프로그램 이름." }
                        }
                      }
                    },
                    "currentTotalWorkOffset": {
                      "type": "object",
                      "description": "공작물 좌표계의 총 오프셋 정보.",
                      "properties": {
                        "workOffsetIndex": { "type": "integer", "description": "G 코드 인덱스." },
                        "workOffsetValue": {
                          "type": "array",
                          "description": "축별 총 오프셋 값. {workOffsetValue=k}",
                          "items": { "type": "number" }
                        },
                        "workOffsetRotation": {
                          "type": "array",
                          "description": "축별 총 회전 오프셋 값. {workOffsetRotation=k}",
                          "items": { "type": "number" }
                        },
                        "workOffsetScalingFactor": {
                          "type": "array",
                          "description": "축별 총 스케일링 값. {workOffsetScalingFactor=k}",
                          "items": { "type": "number" }
                        },
                        "workOffsetMirroringEnabled": {
                          "type": "array",
                          "description": "축별 미러링 활성화 여부. {workOffsetMirroringEnabled=k}",
                          "items": { "type": "boolean" }
                        }
                      }
                    },
                    "currentFile": {
                      "type": "object",
                      "description": "현재 실행 중인 프로그램 파일 정보.",
                      "properties": {
                        "programName": { "type": "string", "description": "파일명." },
                        "programPath": { "type": "string", "description": "파일 경로." },
                        "programSize": { "type": "number", "description": "파일 크기 (byte)." },
                        "programDate": { "type": "string", "description": "파일 생성 날짜." },
                        "programNameWithPath": { "type": "string", "description": "경로를 포함한 전체 파일명." }
                      }
                    },
                    "mainFile": {
                      "type": "object",
                      "description": "현재 선택된(실행 중이 아닐 수 있는) 프로그램 파일 정보.",
                      "properties": {
                        "programName": { "type": "string", "description": "파일명." },
                        "programPath": { "type": "string", "description": "파일 경로." },
                        "programSize": { "type": "number", "description": "파일 크기 (byte)." },
                        "programDate": { "type": "string", "description": "파일 생성 날짜." },
                        "programNameWithPath": { "type": "string", "description": "경로를 포함한 전체 파일명." }
                      }
                    },
                    "controlOption": {
                      "type": "object",
                      "description": "프로그램 실행 제어 옵션.",
                      "properties": {
                        "singleBlock": { "type": "boolean", "description": "싱글 블록 실행 여부." },
                        "dryRun": { "type": "boolean", "description": "드라이 런 실행 여부." },
                        "optionalStop": { "type": "boolean", "description": "옵셔널 스톱(M01) 활성화 여부." },
                        "blockSkip": {
                          "type": "array",
                          "description": "블록 스킵 활성화 여부 리스트. {blockSkip=k}",
                          "items": { "type": "boolean" }
                        },
                        "machineLock": { "type": "boolean", "description": "머신 락 활성화 여부." }
                      }
                    }
                  }
                },
                "workOffset": {
                  "type": "array",
                  "description": "공작물 좌표계 오프셋 정보 리스트. {workOffset=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                      "workOffsetValue": {
                        "type": "array",
                        "description": "축별 오프셋 값. {workOffsetValue=l}",
                        "items": { "type": "number" }
                      },
                      "workOffsetRotation": {
                        "type": "array",
                        "description": "축별 오프셋 회전량 (SIEMENS 전용). {workOffsetRotation=l}",
                        "items": { "type": "number" }
                      },
                      "workOffsetScalingFactor": {
                        "type": "array",
                        "description": "축별 오프셋 확장량 (SIEMENS 전용). {workOffsetScalingFactor=l}",
                        "items": { "type": "number" }
                      },
                      "workOffsetMirroringEnabled": {
                        "type": "array",
                        "description": "축별 미러링 활성화 여부 (SIEMENS 전용). {workOffsetMirroringEnabled=l}",
                        "items": { "type": "boolean" }
                      },
                      "workOffsetFine": {
                        "type": "array",
                        "description": "축별 오프셋 Fine 값 (SIEMENS 전용). {workOffsetFine=l}",
                        "items": { "type": "number" }
                      }
                    }
                  }
                },
                "alarm": {
                  "type": "array",
                  "description": "발생한 알람 정보 리스트. {alarm=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                      "alarmText": { "type": "string", "description": "알람 상세 내용." },
                      "alarmCategory": { "type": "string", "description": "알람 유형." },
                      "alarmNumber": { "type": "string", "description": "알람 번호." },
                      "raisedTimeStamp": { "type": "string", "description": "알람 발생 시각." }
                    }
                  }
                },
                "variable": {
                  "type": "array",
                  "description": "사용자 변수(매크로 변수) 리스트. {variable=k}",
                  "items": {
                    "type": "object",
                    "properties": { "userVariable": { "type": "number", "description": "사용자 변수 값." } }
                  }
                }
              }
            }
          },
          "pic": {
            "type": "object",
            "description": "CNC 내부 PLC 메모리 데이터 모델.",
            "properties": {
              "memory": {
                "type": "object",
                "description": "{machine=i}",
                "properties": {
                  "rbitBlock": { "type": "array", "description": "읽기 전용 Bit 데이터 블록. {rbitBlock=j}", "items": { "type": "boolean" } },
                  "bitBlock": { "type": "array", "description": "읽기/쓰기 가능 Bit 데이터 블록. {bitBlock=j}", "items": { "type": "boolean" } },
                  "rbyteBlock": { "type": "array", "description": "읽기 전용 Byte 데이터 블록. {rbyteBlock=j}", "items": { "type": "integer" } },
                  "byteBlock": { "type": "array", "description": "읽기/쓰기 가능 Byte 데이터 블록. {byteBlock=j}", "items": { "type": "integer" } },
                  "rwordBlock": { "type": "array", "description": "읽기 전용 Word(2byte) 데이터 블록. {rwordBlock=j}", "items": { "type": "integer" } },
                  "wordBlock": { "type": "array", "description": "읽기/쓰기 가능 Word(2byte) 데이터 블록. {wordBlock=j}", "items": { "type": "integer" } },
                  "rdwordBlock": { "type": "array", "description": "읽기 전용 DWord(4byte) 데이터 블록. {rdwordBlock=j}", "items": { "type": "integer" } },
                  "dwordBlock": { "type": "array", "description": "읽기/쓰기 가능 DWord(4byte) 데이터 블록. {dwordBlock=j}", "items": { "type": "integer" } },
                  "rqwordBlock": { "type": "array", "description": "읽기 전용 QWord(8byte) 데이터 블록. {rqwordBlock=j}", "items": { "type": "integer" } },
                  "qwordBlock": { "type": "array", "description": "읽기/쓰기 가능 QWord(8byte) 데이터 블록. {qwordBlock=j}", "items": { "type": "integer" } }
                }
              }
            }
          },
          "toolArea": {
            "type": "array",
            "description": "공구 영역 정보 리스트. {toolArea=j}",
            "items": {
              "type": "object",
              "properties": {
                "toolAreaEnabled": { "type": "boolean", "description": "해당 공구 영역 사용 가능 여부." },
                "numberOfMagazines": { "type": "integer", "description": "사용 가능한 매거진 개수." },
                "numberOfRegisteredTools": { "type": "integer", "description": "공구 영역에 등록된 총 공구 개수." },
                "numberOfLoadedTools": { "type": "integer", "description": "매거진에 탑재된 총 공구 개수." },
                "numberOfToolGroups": { "type": "integer", "description": "등록된 공구 그룹의 개수." },
                "numberOfToolOffsets": { "type": "integer", "description": "등록된 공구 오프셋의 개수." },
                "magazine": {
                  "type": "array",
                  "description": "매거진 정보 리스트. {magazine=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                      "magazineEnabled": { "type": "boolean", "description": "해당 매거진 사용 가능 여부." },
                      "magazineName": { "type": "string", "description": "매거진 이름 (SIEMENS 전용)." },
                      "numberOfRealLocations": { "type": "integer", "description": "매거진의 물리적 포트(위치) 개수." },
                      "magazinePhysicalNumber": { "type": "integer", "description": "매거진의 물리적 번호." },
                      "numberOfLoadedTools": { "type": "integer", "description": "해당 매거진에 탑재된 공구 개수." }
                    }
                  }
                },
                "tools": {
                  "type": "array",
                  "description": "공구 번호 기준 공구 정보 리스트. {tools=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                       "locationNumber": { "type": "integer", "description": "공구가 매거진에 탑재된 위치 번호." },
                       "toolName": { "type": "string", "description": "공구 이름." },
                       "numberOfEdges": { "type": "integer", "description": "공구 날의 총 개수." },
                       "toolEnabled": { "type": "integer", "description": "공구 영역 등록 및 매거진 탑재 여부." },
                       "magazineNumber": { "type": "integer", "description": "공구가 탑재된 매거진 번호." },
                       "sisterToolNumber": { "type": "integer", "description": "할당된 대체 공구 번호." },
                       "toolLifeUnit": { "type": "integer", "description": "공구 수명 측정 단위 기준." },
                       "toolGroupNumber": { "type": "array", "items": { "type": "integer" }, "description": "공구가 참조된 공구 그룹 번호 리스트." },
                       "toolUseOrderNumber": { "type": "integer", "description": "그룹 내 공구 사용 순서 (FANUC 전용)." },
                       "toolStatus": { "type": "integer", "description": "공구의 사용 상태." },
                      "toolEdge": {
                        "type": "array",
                        "description": "공구 날 정보 리스트. {toolEdge=l}",
                        "items": {
                          "type": "object",
                          "properties": {
                             "toolType": { "type": "integer", "description": "공구 유형." },
                             "lengthOffsetNumber": { "type": "integer", "description": "공구 길이 보정 식별 번호." {lengthOffsetNumber=m : m번째 공구 그룹}},
                             "geoLengthOffset": { "type": "number", "description": "공구 길이 X 보정값." {geoLengthOffset=m : m번째 공구 그룹},
                             "wearLengthOffset": { "type": "number", "description": "공구 길이 X 마모 보정값." {wearLengthOffset=m : m번째 공구 그룹}},
                             "radiusOffsetNumber": { "type": "integer", "description": "공구 반경 보정 식별 번호."{radiusOffsetNumber=m : m번째 공구 그룹} },
                             "geoRadiusOffset": { "type": "number", "description": "공구 반경 보정값." {geoRadiusOffset=m : m번째 공구 그룹}},
                             "wearRadiusOffset": { "type": "number", "description": "공구 반경 마모 보정값." {wearRadiusOffset=m : m번째 공구 그룹}},
                             "edgeEnabled": { "type": "boolean", "description": "공구 날 사용 가능 여부." },
                             "geoLengthOffsetZ": { "type": "number", "description": "공구 길이 Z 보정값." {geoLengthOffsetZ=m : m번째 공구 그룹}},
                             "wearLengthOffsetZ": { "type": "number", "description": "공구 길이 Z 마모 보정값." {wearLengthOffsetZ=m : m번째 공구 그룹}},
                             "geoLengthOffsetY": { "type": "number", "description": "공구 길이 Y 보정값." {geoLengthOffsetY=m : m번째 공구 그룹}},
                             "wearLengthOffsetY": { "type": "number", "description": "공구 길이 Y 마모 보정값." {wearLengthOffsetY=m : m번째 공구 그룹}},
                             "geoOffsetNumber": { "type": "integer", "description": "길이 X,Z, 반경의 식별 번호." {geoOffsetNumber=m : m번째 공구 그룹}},
                             "wearOffsetNumber": { "type": "integer", "description": "길이 X,Z, 반경 마모값의 식별 번호." {wearOffsetNumber=m : m번째 공구 그룹}},
                             "cuttingEdgePosition": { "type": "integer", "description": "공구 인선 방향." {cuttingEdgePosition=m : m번째 공구 그룹}},
                             "tipAngle": { "type": "number", "description": "공구의 팁 각도." },
                             "holderAngle": { "type": "number", "description": "공구 홀더 각도." },
                             "insertAngle": { "type": "number", "description": "공구 인서트 각도." },
                             "insertWidth": { "type": "number", "description": "인선 너비 (SIEMENS 전용)." },
                             "insertLength": { "type": "number", "description": "인선 길이 (SIEMENS 전용)." },
                             "referenceDirectionHolderAngle": { "type": "number", "description": "홀더 각도 참조 방향 (SIEMENS 전용)." },
                             "directionOfSpindleRotation": { "type": "integer", "description": "스핀들 회전 방향 (SIEMENS 전용)." },
                             "numberOfTeeth": { "type": "integer", "description": "공구 날 개수 (SIEMENS 전용)." },
                            "toolLife": {
                              "type": "object",
                              "description": "공구 수명 정보 (읽기/쓰기 가능).",
                              "properties": {
                                "maxToolLife": { "type": "number", "description": "최대 공구 수명." {maxToolLife = m : m번째 공구 그룹}},
                                "restToolLife": { "type": "number", "description": "잔여 공구 수명." {restToolLife = m : m번째 공구 그룹}},
                                "toolLifeCount": { "type": "number", "description": "현재 공구 사용량." {toolLifeCount = m : m번째 공구 그룹}},
                                "toolLifeAlarm": { "type": "number", "description": "공구 수명 도달 경고 설정값." }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                },
                "registerTools": {
                  "type": "array",
                  "description": "등록 순서 기준 공구 정보 리스트. {registerTools=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                       "locationNumber": { "type": "integer", "description": "공구가 매거진에 탑재된 위치 번호." },
                       "toolName": { "type": "string", "description": "공구 이름." },
                       "numberOfEdges": { "type": "integer", "description": "공구 날의 총 개수." },
                       "toolEnabled": { "type": "integer", "description": "공구 영역 등록 및 매거진 탑재 여부." },
                       "magazineNumber": { "type": "integer", "description": "공구가 탑재된 매거진 번호." },
                       "sisterToolNumber": { "type": "integer", "description": "할당된 대체 공구 번호." },
                       "toolLifeUnit": { "type": "integer", "description": "공구 수명 측정 단위 기준." },
                       "toolGroupNumber": { "type": "array", "items": { "type": "integer" }, "description": "공구가 참조된 공구 그룹 번호 리스트." },
                       "toolUseOrderNumber": { "type": "integer", "description": "그룹 내 공구 사용 순서 (FANUC 전용)." },
                       "toolStatus": { "type": "integer", "description": "공구의 사용 상태." },
                      "toolEdge": {
                        "type": "array",
                        "description": "공구 날 정보 리스트. {toolEdge=l}",
                        "items": {
                          "type": "object",
                          "properties": {
                             "toolType": { "type": "integer", "description": "공구 유형." },
                             "lengthOffsetNumber": { "type": "integer", "description": "공구 길이 보정 식별 번호." {lengthOffsetNumber=m : m번째 공구 그룹}},
                             "geoLengthOffset": { "type": "number", "description": "공구 길이 X 보정값."{geoLengthOffset=m : m번째 공구 그룹} },
                             "wearLengthOffset": { "type": "number", "description": "공구 길이 X 마모 보정값."{wearLengthOffset=m : m번째 공구 그룹}},
                             "radiusOffsetNumber": { "type": "integer", "description": "공구 반경 보정 식별 번호." {radiusOffsetNumber=m : m번째 공구 그룹}},
                             "geoRadiusOffset": { "type": "number", "description": "공구 반경 보정값."{geoRadiusOffset=m : m번째 공구 그룹}},
                             "wearRadiusOffset": { "type": "number", "description": "공구 반경 마모 보정값."{wearRadiusOffset=m : m번째 공구 그룹}},
                             "edgeEnabled": { "type": "boolean", "description": "공구 날 사용 가능 여부." },
                             "geoLengthOffsetZ": { "type": "number", "description": "공구 길이 Z 보정값."{geoLengthOffsetZ=m : m번째 공구 그룹} },
                             "wearLengthOffsetZ": { "type": "number", "description": "공구 길이 Z 마모 보정값."{wearLengthOffsetZ=m : m번째 공구 그룹} },
                             "geoLengthOffsetY": { "type": "number", "description": "공구 길이 Y 보정값."{geoLengthOffsetY=m : m번째 공구 그룹} },
                             "wearLengthOffsetY": { "type": "number", "description": "공구 길이 Y 마모 보정값." {wearLengthOffsetY=m : m번째 공구 그룹}},
                             "geoOffsetNumber": { "type": "integer", "description": "길이 X,Z, 반경의 식별 번호." {geoOffsetNumber=m : m번째 공구 그룹}},
                             "wearOffsetNumber": { "type": "integer", "description": "길이 X,Z, 반경 마모값의 식별 번호." {wearOffsetNumber=m : m번째 공구 그룹}},
                             "cuttingEdgePosition": { "type": "integer", "description": "공구 인선 방향." {cuttingEdgePosition=m : m번째 공구 그룹}},
                             "tipAngle": { "type": "number", "description": "공구의 팁 각도." },
                             "holderAngle": { "type": "number", "description": "공구 홀더 각도." },
                             "insertAngle": { "type": "number", "description": "공구 인서트 각도." },
                             "insertWidth": { "type": "number", "description": "인선 너비 (SIEMENS 전용)." },
                             "insertLength": { "type": "number", "description": "인선 길이 (SIEMENS 전용)." },
                             "referenceDirectionHolderAngle": { "type": "number", "description": "홀더 각도 참조 방향 (SIEMENS 전용)." },
                             "directionOfSpindleRotation": { "type": "integer", "description": "스핀들 회전 방향 (SIEMENS 전용)." },
                             "numberOfTeeth": { "type": "integer", "description": "공구 날 개수 (SIEMENS 전용)." },
                            "toolLife": {
                              "type": "object",
                              "description": "공구 수명 정보 (읽기/쓰기 가능).",
                              "properties": {
                                "maxToolLife": { "type": "number", "description": "최대 공구 수명." {maxToolLife = m : m번째 공구 그룹}},
                                "restToolLife": { "type": "number", "description": "잔여 공구 수명."{restToolLife = m : m번째 공구 그룹} },
                                "toolLifeCount": { "type": "number", "description": "현재 공구 사용량."  {toolLifeCount = m : m번째 공구 그룹},
                                "toolLifeAlarm": { "type": "number", "description": "공구 수명 도달 경고 설정값." }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "buffer": {
            "type": "array",
            "description": "시계열 데이터 수집 버퍼 정보 리스트. {buffer=j}",
            "items": {
              "type": "object",
              "properties": {
                "bufferEnabled": { "type": "boolean", "description": "해당 버퍼 사용 가능 여부." },
                "numberOfStream": { "type": "integer", "description": "해당 버퍼의 최대 스트림 개수." },
                "statusOfStream": { "type": "integer", "description": "스트림 상태 (0: 설정 가능, 3: 수집 중 등)." },
                "modOfStream": { "type": "integer", "description": "스트림 수집 모드 (0: 반복 수집, 1: 1회 수집)." },
                "machineChannelOfStream": { "type": "integer", "description": "스트림 수집 시 사용할 채널." },
                "periodOfStream": { "type": "integer", "description": "1회 수집 기간 (단위: ms)." },
                "triggerOfStream": { "type": "integer", "description": "수집 시작 트리거 (0: 즉시, 1이상: 시퀀스 번호)." },
                "frequencyOfStream": { "type": "integer", "description": "모든 스트림에 공통으로 적용할 수집 주파수 (Hz)." },
                "stream": {
                  "type": "array",
                  "description": "개별 센서 데이터 스트림 채널 리스트. {stream=k}",
                  "items": {
                    "type": "object",
                    "properties": {
                      "streamEnabled": { "type": "boolean", "description": "해당 스트림 사용 가능 여부." },
                      "streamFrequency": { "type": "integer", "description": "해당 스트림의 수집 주파수 (Hz)." },
                      "streamCategory": { "type": "integer", "description": "수집 대상 데이터 카테고리." },
                      "streamSubcategory": { "type": "integer", "description": "수집 대상 데이터 서브카테고리 (축/스핀들 번호 등)." },
                      "streamType": { "type": "integer", "description": "수집 유형 (KCNC 전용)." },
                      "streamStartBit": { "type": "integer", "description": "수집 유형이 Bit일 때 Start Bit (KCNC 전용)." },
                      "streamEndBit": { "type": "integer", "description": "수집 유형이 Bit일 때 End Bit (KCNC 전용)." },
                      "value": { "type": "number", "description": "해당 스트림에서 마지막으로 수집된 데이터 값." }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}


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