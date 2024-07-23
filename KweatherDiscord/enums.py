from __future__ import annotations
from enum import Enum

__all__ = (
    "KoreaWeatherEnum",
    "ForecastDict"
)

class KoreaWeatherEnum(str, Enum):
    NORMAL_SERVICE = "00"
    APPLICATION_ERROR = "01"
    DB_ERROR = "02"
    NODATA_ERROR = "03"
    HTTP_ERROR = "04"
    SERVICETIME_OUT = "05"
    INVALID_REQUEST_PARAMETER_ERROR = "10"
    NO_MANDATORY_REQUEST_PARAMETERS_ERROR = "11"
    NO_OPENAPI_SERVICE_ERROR = "12"
    SERVICE_ACCESS_DENIED_ERROR = "20"
    TEMPORARILY_DISABLE_THE_SERVICEKEY_ERROR = "21"
    LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR = "22"
    SERVICE_KEY_IS_NOT_REGISTERED_ERROR = "30"
    DEADLINE_HAS_EXPIRED_ERROR = "31"
    UNREGISTERED_IP_ERROR = "32"
    UNSIGNED_CALL_ERROR = "33"
    UNKNOWN_ERROR = "99"


ForecastDict = {
    "RN1" : ['1시간 강수량'],
    "PTY" : ['강수형태'],
    "VEC" : ['풍향'],
    "SKY" : ['하늘상태'],
    "PCP" : ['1시간 강수량'],
    # 여기서부터는 단위가 있는 것들입니다.
    "UUU" : ['동서바람성분', 'm/s'],
    "VVV" : ['남북바람성분', 'm/s'],
    "REH" : ['습도', '%'],
    "WSD" : ['풍속', 'm/s'],
    "LGT" : ['낙뢰', 'kA/㎢'],
    "POP" : ['강수확률', '%'],
    "SNO" : ['1시간 적설량', 'cm'],
    "T1H" : ['기온', '℃'],
    "TMP" : ['기온', '℃'],
    "TMN" : ['최저기온', '℃'],
    "TMX" : ['최고기온', '℃'],
    "WAV" : ['파고', 'm']
}