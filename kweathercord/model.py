from __future__ import annotations
from .enums import KoreaWeatherEnum
from pydantic import BaseModel
from typing import (
    Any,
    Generator,
    List,
    Literal,
    NamedTuple,
    Optional,
    Union
)


class SimilarityInfo(NamedTuple):
    full_name : str
    score : float


class LocationInfo(NamedTuple):
    full_name : str
    nx : int
    ny : int
    latitude : float
    longitude : float


NowForecastStatus = Literal['T1H', 'RN1', 'UUU', 'VVV', 'REH', 'PTY', 'VEC', 'WSD']
ShortForecastStatus = Literal['POP', 'PTY', 'PCP', 'REH', 'SNO', 'SKY', 'TMP', 'TMN', 'TMX', 'UUU', 'VVV', 'WAV', 'VEC', 'WSD']
UltraShortForecastStatus = Literal['T1H', 'RN1', 'SKY', 'UUU', 'VVV', 'REH', 'PTY', 'LGT', 'VEC', 'WSD']


class ForecastInputBase(BaseModel):
    """Request 시 필요한 파라미터들입니다."""
    serviceKey : str
    numOfRows : int = 10
    pageNo : int = 1
    dataType : Literal['XML', 'JSON'] = 'XML'
    base_date : str
    base_time : str
    nx : int
    ny : int


class ForecastResponseModel(BaseModel):
    """응답 전체모델입니다.
    헤더와 바디로 나뉘어져 있으며, 바디는 응답 실패 시, None으로 반환될 수 있습니다."""
    header : ForecastResponseHeader
    body : Optional[ForecastResponseBody] = None


class ForecastResponseHeader(BaseModel):    
    """응답 헤더 모델입니다."""
    resultCode : KoreaWeatherEnum
    resultMsg : str


class ForecastResponseBody(NamedTuple):
    """응답 바디 모델입니다."""
    dataType : str
    items : ForecastItems
    pageNo : int
    numOfRows : int
    totalCount : int


class ForecastItems(NamedTuple):
    """날씨 정보를 담은 객체입니다.
    정상 응답 시 `List[Dict[str, Any]]`꼴로 반환하나, 메모리 절약을 위해 제너레이터 객체로 대신합니다.
    """
    item : WeatherGen


class BaseResponseItem(BaseModel):
    baseDate : str
    baseTime : str
    nx : int
    ny : int


class NowWeatherItem(BaseResponseItem):
    category : NowForecastStatus
    obsrValue : str


class BaseShortWeatherItem(BaseResponseItem):
    fcstDate : str
    fcstTime : str


class UltraShortWeatherItem(BaseShortWeatherItem):
    category : UltraShortForecastStatus
    fcstValue : str


class ShortWeatherItem(BaseShortWeatherItem):
    category : ShortForecastStatus
    fcstValue : str


WeatherGen = Generator[
    Union[NowWeatherItem, UltraShortWeatherItem, ShortWeatherItem],
    None,
    None
]


class TimeWeather(NamedTuple):
    """시간대별로 날씨 정보를 딕셔너리로 담은 객체입니다."""
    time : str
    weather : dict[str, Any]


class DateTimeWeather(NamedTuple):
    """날짜별로 TimeWeather 정보가 담긴 객체입니다."""
    date : str
    time_weather : Generator[TimeWeather, None, None]


class WeatherResult(NamedTuple):
    """도시명과 날씨 정보를 반환합니다."""
    city_name : str
    weather : List[DateTimeWeather, None, None]