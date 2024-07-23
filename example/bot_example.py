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
    
    async def setup_hook(self) -> None:
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
