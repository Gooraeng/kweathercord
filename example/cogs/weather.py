from discord import app_commands, Interaction
from discord.ext import commands
from typing import Literal

from bot_example import Test   


class Weather(commands.Cog):
    def __init__(self, bot : Test) -> None:
        self.bot = bot
        
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
            await self.bot.weather.get_weather(interaction, method=method, city=where, hidden=True)

        except Exception as e:
            # interaction.response.defer를 사용하기 때문에,
            # 오류 발생 시, Interaction.Followup 이나 InteractionMessage만 허용됩니다.
            await interaction.followup.send(e)


async def setup(bot : Test):
    await bot.add_cog(Weather(bot))