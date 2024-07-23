from discord import app_commands, Interaction
from discord.ext import commands
from typing import TYPE_CHECKING, Literal
# import 경로에 따라 적절하게 조절해야 합니다
from KweatherDiscord import KoreaForecastForDiscord

if TYPE_CHECKING:
    from bot_example import BotTest


class Weather(commands.Cog):
    def __init__(self, bot : BotTest) -> None:
        self.bot = bot
        # "setup_hook 함수 내"에서 선언할 수 있다면 상관없습니다.
        self.weather = KoreaForecastForDiscord(self.bot)
    
    # commands.Context는 사용하지 않습니다.
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
            
        except Exception:
            ...


async def setup(bot : BotTest):
    await bot.add_cog(Weather(bot))