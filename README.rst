KweatherDiscord
===============

- KweatherDiscord은 대한민국 기상청 API을 이용하여 대한민국의 날씨를 Embed, Button, Select Menu를 이용하여 확인하는 간단한 도구입니다.
- 초단기실황, 초단기예보, 단기예보를 지원합니다.
- NOAA 알고리즘을 통해 조회하시는 지역의 일출, 일몰 시간에 맞추어 아이콘이 조정됩니다.

구현 모습
---------------
.. image:: example/results/weather1.png
    :width: 400


파이썬 요구 사항
------------------

.. note::
   - Python 3.8 이상에서 작동합니다.


의존 패키지
----------------
- Discord.py (2.4.0 이상)
- pydantic
- RapidFuzz


설치 방법
--------------

- 설치 시
.. code:: sh

    pip install -U kweather-cord

- 업그레이드 시
.. code:: sh

    pip install kweather-cord --upgrade


제한 사항
-------------
- 당일, 최저/최고 온도는 제공하지 않으나 초단기예보 및 단기예보에서 각각 06시와 15시를 최저/최고온도로 지정하고 있습니다. 초단기실황은 지원하지 않습니다.
- 이 패키지는 discord.py의 app_commands 모듈(Slash command)의 사용을 권장합니다.
- 또, 안정적인 동작을 위해, defer가 적용되어 있습니다. Error Handling 시, edit_original_response나 followup.send 메소드 사용을 고려해주십시오.


사용 예시
-------------

1. bot.py
~~~~~~~~~~~~

.. code:: py

    from aiohttp import ClientSession
    from discord.ext import commands
    from kweathercord import KoreaForecastForDiscord

    import discord

    initial_extensions = (
        'cogs.weather',
    )


    class Test(commands.Bot):
        def __init__(self):
            intents = discord.Intents.default()
            super().__init__(
                command_prefix='!',
                intents=intents
            )
        
        async def setup_hook(self):
            # aiohttp 사용을 위한 선언 (라이브러리 한계로 인해 동기 함수에서 선언할 수 없습니다.)
            # 반드시 아래와 같이 선언해주어야 합니다.
            self.session = ClientSession()
            for extension in initial_extensions:
                try:
                    await self.load_extension(extension)
                except Exception:
                    raise
            # await self.tree.sync()
        
        async def on_ready(self):
            ...
            # on_ready에서 사용해도 되나, 이 함수에서 복잡한 작업은 권장되지 않습니다.
            # 따라서, setup_hook 함수 내에서 이루어지는 것이 좋습니다.


2. cog.weather
~~~~~~~~~~~~~~~~

.. code:: py

    from discord import app_commands, Interaction
    from discord.ext import commands
    from typing import TYPE_CHECKING, Literal
    from kweathercord import KoreaForecastForDiscord
    from bot_example import Test   


    class Weather(commands.Cog):
        def __init__(self, bot : Test):
            self.bot = bot
            # "setup_hook 함수 내"에서 선언할 수 있다면 상관없습니다.
            # 여기서 선언하는 것도 setup_hook 내에서 선언하는 것과 같습니다.
            self.weather = KoreaForecastForDiscord(self.bot)
        
        # commands.Context는 가급적 사용하지 않습니다.
        @app_commands.command(name='날씨', description='지역의 날씨를 찾아보세요')
        @app_commands.describe(
            where='어느 지역의 날씨를 검색하실 건가요?',
            period='어떤 검색 방식을 이용하실 건가요?'
        )
        @app_commands.rename(where='지역', period='기간')
        async def search(self, interaction : Interaction, where : str, period : Literal['지금', '향후 6시간', '향후 3~4일']):
            try:
                if period == '지금':
                    method == '초단기실황'
                elif period == '향후 3~4일':
                    method = '단기예보'
                else:
                    method = '초단기예보'
                await self.weather.get_weather(interaction, method=method, city=where)
                
            except Exception as e:
                # interaction.response.defer를 사용하기 때문에,
                # 오류 발생 시, Interaction.Followup 이나 InteractionMessage만 허용됩니다.
                await interaction.followup.send(e)


async def setup(bot : Test):
    await bot.add_cog(Weather(bot))


참고 링크
--------

- `대한민국 기상청 API <https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15084084>`_