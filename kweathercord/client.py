from __future__ import annotations
import aiohttp.client_exceptions
from aiohttp.typedefs import StrOrURL
from rapidfuzz.process import extractOne
from typing import (
    ClassVar,
    Literal,
    Optional,
)
from .enums import ForecastDict
from .exception import LocationNotFound, WeatherResponseException
from .model import (
    DateTimeWeather,
    ForecastInputBase,
    LocationInfo,
    NowWeatherItem,
    ShortWeatherItem,
    SimilarityInfo,
    TimeWeather,
    UltraShortWeatherItem,
    WeatherGen,
    WeatherResult,
)
from .sun_riseset_time import calculate_sunset_sunrise
from .view import WeatherPages

import asyncio
import aiohttp
import datetime
import discord
import json
import math
import os
import pathlib
import re


class KoreaForecastForDiscord:
    """디스코드 봇 전용으로 만들어진 클래스입니다."""
    
    BASE : ClassVar[str] = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/"

    def __init__(self, bot) -> None:
        self.bot = bot
        self.__serviceKey : Optional[str] = os.getenv('serviceKey')
        self.__lock = asyncio.Lock()
        self.__url : Optional[str] = None
        self.__item = self.__generate_items()
     
    def __generate_items(self):
        file = pathlib.Path(__file__).parent.resolve() / 'area/weather_area.json'
        with open(file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        data = [
            LocationInfo(
                full_name=item['full_name'],
                nx=item['nx'],
                ny=item['ny'],
                latitude=item['latitude'],
                longitude=item['longitude']
            ) for item in data
        ]
        return data
    
    def check_korean(self, string : str):
        result = re.fullmatch(r'[가-힣0-9., ]*$', string)
        if result:
            return True
        return False
    
    async def get_weather(
        self,
        interaction : discord.Interaction,
        *,
        method : Literal['초단기실황', '초단기예보', '단기예보'],
        city : str,
        hidden : bool = True,
    ) :
        """검색하고자 하는 도시의 날씨를 검색합니다. 그리고나서, 임베딩 페이지를 보여줍니다.
        `Button`: 날짜를 선택하는 버튼입니다. 초단기 실황에서만 나타나지 않습니다.
        `Select`: 시간을 선택하는 메뉴입니다. 초단기 실황에서만 나타나지 않습니다.
        
        ## Args:
        * `interaction (discord.Interaction)` : discord.Interaction입니다.
        * `method` : 어떤 방식으로 검색하실건가요?\n
            (1) '초단기실황' : 현재 시간을 기준으로 검색합니다.
            (2) '초단기예보' : 검색 시간 기준, 향후 6시간까지를 검색합니다.
            (3) '단기예보' : 향후 약 3일 간 날씨를 검색합니다.
        * `city (str)` : 당신이 입력하여 찾고자 하는 곳입니다.
        * `hidden (bool)` : 답장 메세지가 다른 사람에게 보이게 할 것인지 결정합니다. 미지정 시 False로 정합니다.
        
        ## Raise:
            `ValueError` : 적절하지 않은 값이 투입되었을 때, 발생합니다.
            `LocationNotFound` : 장소 검색에 실패했을 시에 발생합니다. 유사 장소 최대 5곳을 반환합니다.
            `WeatherResponseException` : 기상청 API 응답 헤더로부터 발생되는 오류입니다.
            `aiohttp.ClientError` : Aiohttp 라이브러리와 관련된 오류 발생 시 반환합니다.
        """
        try:
            # 안정성을 위해 defer를 사용합니다. thinking = true 시 최대 15분 간 응답 대기를 합니다.
            await interaction.response.defer(thinking=True, ephemeral=hidden)
            if not self.check_korean(city):
                raise ValueError("오로지 한국어 / ',' /' '/ '.'만 사용할 수 있습니다.")
            
            if method == '단기예보':
                numOfRows = 1000
            else:
                numOfRows = 30
            
            async with self.__lock:
                location = self._get_coordinate(city)
            
            entries = await self._configure_request(
                method=method,
                location=location,
                numOfRows=numOfRows,
            )
            page = WeatherPages(entries=entries, author=interaction.user, hidden=hidden)
            await page.start(interaction)
        
        except (ValueError, LocationNotFound, WeatherResponseException):
            raise
        
        except aiohttp.ClientError:
            raise aiohttp.ClientError('알 수 없는 HTTP 오류가 발생했습니다. 다시 시도해주십시오.')

    async def _configure_request(
        self,
        method : Literal['초단기실황', '초단기예보', '단기예보'],
        location : LocationInfo,
        numOfRows : int = 10,
        pageNo : int = 1,
    ) -> WeatherResult :
        KST = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
        
        def get_time_by_method(method):
            match method:
                case '초단기실황':
                    self.__url = self.BASE + 'getUltraSrtNcst'
                    if KST.minute >= 40:
                        finalDatetime = KST.replace(minute=0)
                    else:
                        finalDatetime = KST.replace(minute=0) - datetime.timedelta(hours=1)

                case '초단기예보':
                    self.__url = self.BASE + 'getUltraSrtFcst'
                    if KST.minute >= 45:
                        finalDatetime = KST.replace(minute=30)
                    else:
                        finalDatetime = KST.replace(minute=30) - datetime.timedelta(hours=1)
                
                case '단기예보':
                    self.__url = self.BASE + 'getVilageFcst'
                    hour = KST.hour
                    if 0 <= hour < 2:
                        finalDatetime = KST.replace(hour=23, minute=10) - datetime.timedelta(days=1)
                    elif 2 <= hour < 5:
                        finalDatetime = KST.replace(hour=2, minute=10)
                    elif 5 <= hour < 8:
                        finalDatetime = KST.replace(hour=5, minute=10)
                    elif 8 <= hour < 11:
                        finalDatetime = KST.replace(hour=8, minute=10)
                    elif 11 <= hour < 14:
                        finalDatetime = KST.replace(hour=11, minute=10)
                    elif 14 <= hour < 17:
                        finalDatetime = KST.replace(hour=14, minute=10)
                    elif 17 <= hour < 20:
                        finalDatetime = KST.replace(hour=17, minute=10)
                    elif 20 <= hour < 23:
                        finalDatetime = KST.replace(hour=20, minute=10)
                    else:
                        finalDatetime = KST.replace(hour=23, minute=10)
                
            return finalDatetime
        
        async with self.__lock:
            FINAL_TIME = get_time_by_method(method)                                 
            base_date = FINAL_TIME.strftime('%Y%m%d')                 
            base_time = FINAL_TIME.strftime('%H%M')       
        
        params = ForecastInputBase(
            serviceKey=self.__serviceKey,
            numOfRows=numOfRows,
            pageNo=pageNo,
            dataType='JSON',
            base_date=base_date,
            base_time=base_time,
            nx=location.nx,
            ny=location.ny
        )
        
        try:
            payload = await self.__handle_request(self.__url, method=method, params=params, session=self.bot.session)
            return await self.__handle_response(payload, city=location)
    
        except (aiohttp.ClientError, WeatherResponseException):
            raise
    
    async def __handle_response(
        self,
        payload : WeatherGen,
        city : LocationInfo
    ) -> WeatherResult :
        """요청 응답을 적절한 데이터셋으로 재조립합니다.

        ## Args:
            payload `WeatherGen`: 
            city `str`: 검색 결과로 나온 도시명입니다.

        ## Returns:
            WeatherResult: _description_
        """
        def vector_transformer(value):
            q = math.floor((int(value) + 11.25) / 22.5)
            if 2 <= q <= 3:
                return '북동풍'
            elif 4 <= q <= 5:
                return '동풍'
            elif 6 <= q <= 7:
                return '남동풍'
            elif 8 <= q <= 9:
                return '남풍'
            elif 10 <= q <= 11:
                return '남서풍'
            elif 12 <= q <= 13:
                return '서풍'
            elif 14 <= q <= 15:
                return '북서풍'
            return '북풍'
    
        async with self.__lock:         
            weather_dict = {}
            rise_set_date = None
            sunrise = None
            sunset = None
            for item in payload:
                category = item.category
                if category == 'UUU' or category == 'VVV':
                    continue
    
                if isinstance(item, NowWeatherItem):
                    value = item.obsrValue
                    date_dict = weather_dict.setdefault(item.baseDate, {})
                    time_dict = date_dict.setdefault(item.baseTime, {})
                    sunrise, sunset = calculate_sunset_sunrise(item.baseDate, city.latitude, city.longitude)
                    if not rise_set_date or rise_set_date != item.baseDate:
                        rise_set_date = item.baseDate
                        sunrise, sunset = calculate_sunset_sunrise(item.baseDate, city.latitude, city.longitude)
                        
                elif isinstance(item, ShortWeatherItem) or isinstance(item, UltraShortWeatherItem):
                    value = item.fcstValue
                    date_dict = weather_dict.setdefault(item.fcstDate, {})
                    time_dict = date_dict.setdefault(item.fcstTime, {})
                    if not rise_set_date or rise_set_date != item.fcstDate:
                        rise_set_date = item.fcstDate
                        sunrise, sunset = calculate_sunset_sunrise(item.fcstDate, city.latitude, city.longitude)
                        
                factor = ForecastDict[category]
                match category:
                    # 강수 상태
                    case 'PTY':
                        if value == '0':
                            filename = 'clear'
                            if isinstance(item, NowWeatherItem):
                                time = item.baseTime
                            else:
                                time = item.fcstTime
                            if sunset <= time or sunrise > time:
                                filename += '_night'
                        elif value == '1' or value == '5':
                            filename = 'rainy'
                        elif value == '2':
                            filename = 'rainy_snow'
                        elif value == '3' or value == '7':
                            filename = 'snowy'
                        elif value == '4':
                            filename = 'shower'
                        elif value == '6':
                            filename = 'rain_with_snow'
                        time_dict['filename'] = filename
                    
                    case 'SKY':
                        assert isinstance(item, ShortWeatherItem) or isinstance(item, UltraShortWeatherItem)
                        try:
                            if time_dict['filename'] is not None and time_dict['filename'] in ['rainy', 'rainy_snow', 'snowy', 'shower', 'rain_with_snow']:
                                continue
                        except:
                            pass
                        if value == '1':
                            filename = 'clear'
                        elif value == '3':
                            filename = 'partly_cloudy'
                        if (sunset <= item.fcstTime or sunrise > item.fcstTime) and (value == '1' or value == '3'):
                            filename += '_night'
                        if value == '4':
                            filename = 'cloudy'
                        time_dict['filename'] = filename

                    case 'RN1' | 'PCP':
                        if isinstance(item, NowWeatherItem):
                            value = float(value)
                            if 0 >= value or value is None:
                                value = '강수없음'
                            elif 0.1 < value < 1.0:
                                value = '1mm 미만'
                            elif 1.0 <= value < 30.0:
                                value = f'{value}mm'
                            elif 30.0 <= value < 50.0:
                                value = '30 ~ 50mm'
                            else:
                                value = '50mm 이상'
                        time_dict[factor[0]] = value
                        
                    case 'SNO':
                        if isinstance(value, float):
                            if 0 >= value or value is None:
                                value = '적설없음'
                            elif 0.1 < value < 1.0:
                                value = '1cm 미만'
                            elif 1.0 <= value < 5.0:
                                value = f'{value}cm'
                            else:
                                value = '5cm 이상'
                        time_dict[factor[0]] = value
                    
                    case 'VEC':
                        time_dict[factor[0]] = vector_transformer(value)
                        
                    case 'TMX' | 'TMN':
                        continue

                    case _ :
                        if category == 'WAV' and value == '0':
                            continue
                        # 파라미터가 있는 것
                        time_dict[factor[0]] = f'{value}{factor[1]}'

            del payload
            
            datelist = [
                DateTimeWeather(
                    date=date,
                    time_weather=[
                        TimeWeather(time=time, weather=weather)
                        for time, weather in time_weather.items()
                    ]
                )
                for date, time_weather in weather_dict.items()
            ]
            
            del weather_dict
            return WeatherResult(
                city_name=city.full_name,
                weather=datelist
            )

    def _get_coordinate(
        self,
        city : str,
        *,
        score_cutoff : float = 42.5
    ) :
        """입력된 곳을 기준으로, 정의된 유사도 기준 이상의 도시를 검색합니다.
        이 때, 유사도가 가장 높은 도시 한 곳의 격자 좌표(nx, ny)와 좌표(9자리 숫자 문자열)를 반환합니다.
        검색에 실패했을 경우 검색값과 가장 비슷한 장소 최대 5곳을 제안합니다.
        
        ## Args:
        * city `str` : 당신이 입력한 도시입니다.
        * score_cutoff `Optional[Float]` : 0부터 100까지이며, 별도로 지정하지 않았을 경우 82.0으로 지정됩니다.
        
        ## Returns:
            `LocationInfo`
        
        ## Raises:
            `ValueError`: `score_cutoff`가 지정된 범위를 벗어났을 때 발생합니다.
            `LocationNotFound`: 검색에 실패했을 시 발생합니다.        
        """
        if 0.0 > score_cutoff or score_cutoff > 100.0:
            raise ValueError('정확도는 0보다 낮거나 100보다 클 수 없습니다.')

        best_match = None
        highest_score = 0.0
        similar_result : list[SimilarityInfo]= []
        
        for location in self.__item:
            city_sub = re.sub(r'\s+', '', city)
            location_sub = re.sub(r'\s+', '', location.full_name)
            result = extractOne(city_sub, [location_sub], score_cutoff=score_cutoff)
            if not result:
                continue

            score = result[1]
            if score > highest_score:
                highest_score = score
                best_match = location
            else:
                similar_result.append(SimilarityInfo(full_name=location.full_name, score=score))
                
        if best_match and highest_score >= 64:
            return best_match
        
        similar_result = sorted(similar_result, key=lambda x : x.score, reverse=True)
        similar_result = ', '.join(s.full_name for s in similar_result[:5])
        raise LocationNotFound(city, similar=similar_result)

    async def __handle_request(
        self,
        url : StrOrURL,
        *,
        method : Literal['초단기실황', '초단기예보', '단기예보'],
        session : Optional[aiohttp.ClientSession] = None,
        params : ForecastInputBase
    ) -> WeatherGen:
        """기상청 API에 요청을 보냅니다.

        ## Args:
            url : 기상청 API에 Request할 Url입니다.
            method `Literal`: 요청 방식입니다.
            params `ForecastInputBase`: 기상청 API에 정보 요청 시 반드시 들어가야 하는 정보들입니다.
            session `Optional[ClientSession]` : 기본적으로 ClientSession을 씁니다.
        
        ## Returns:
            WeatherGen: 날씨 정보를 담은 제너레이터를 반환합니다.
        
        ## Raises:
            `aiohttp.ClientError`: 요청에 실패할 시 발생합니다.
            `WeatherResponseException`: 요청에는 성공했으나 기상청 API가 어떠한 이유로 정보제공을 거절했는지 알려줍니다.
        """
        if not session:
            session = aiohttp.ClientSession()
        try:
            async with session.get(url, params=params.model_dump()) as res :
                if res.status != 200:
                    raise aiohttp.ClientError
                response = (await res.json())['response']
        except aiohttp.ClientError:
            raise
            
        header : str = response['header']
        if header['resultCode'] != "00":
            raise WeatherResponseException(header)
        
        response_items = response['body']['items']['item']
        
        if method == '초단기실황':
            item = (NowWeatherItem(**s) for s in response_items)        
        elif method == '초단기예보':
            item = (UltraShortWeatherItem(**s) for s in response_items)  
        elif method == '단기예보':
            item = (ShortWeatherItem(**s) for s in response_items)
        return item 