from aiohttp import ClientSession
from discord.ext import commands

import asyncio
import discord


initial_extensions = (
    'cogs.weather'
)


class BotTest(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(
            command_prefix='!',
            intents=intents
        )
    
    async def setup_hook(self) -> None:
        # aiohttp 사용을 위한 선언 (동기 함수에서 선언할 수 없습니다.)
        self.session = ClientSession()
        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception:
                pass
    
    async def on_ready(self):
        ...
        # on_ready에서 사용해도 되나, 이 함수에서 복잡한 작업은 권장되지 않습니다.
        # 따라서, setup_hook 함수 내에서 이루어지는 것이 좋습니다.


async def main():
    async with BotTest() as bot:
        # 토큰 넣기
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())