from __future__ import annotations
from .model import ForecastResponseHeader


class KWeatherException(Exception):
    """KWather.py의 기본 예외 클래스입니다.
    이 라이브러리에서 발생된 모든 예외를 다룹니다.
    """
    pass


class WeatherResponseException(KWeatherException):
    """요청이 실패했을 시 발생되는 예외 클래스입니다."""

    def __init__(self, header : ForecastResponseHeader | str) -> None:
        if isinstance(header, ForecastResponseHeader):
            code = header.resultCode.value
            result = header.resultMsg
        elif isinstance(header, str):
            code = header['resultCode']
            result = header['resultMsg']
        self.message = f'[서비스 에러]\n* Code : {code}\n* 설명 : {result}'
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

class LocationNotFound(KWeatherException):
    """지역 검색에 실패할 시 발생되는 예외 클래스입니다."""
    
    def __init__(self, area : str, *, similar : str = None) -> None:
        if similar:
            similar = f' 혹시 이 지역을 말하는 건가요?\n{similar}'
        else:
            similar = ''
        self.message = f'"{area}" 지역을 찾을 수 없습니다.{similar}'
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return self.message