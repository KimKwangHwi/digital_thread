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