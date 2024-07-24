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
        # Kweathercord는 clientsession을 선언하지 않아도, 라이브러리에서 핸들링 할 수 있습니다.
        self.session = ClientSession()
        self.weather = KoreaForecastForDiscord(self)
        # 만약 봇 자체 클래스에서 aiohttp.ClientSession이 선언된 게 있다면,
        # 아래의 방식을 이용해주세요.
        self.weather.session = self.session
        # 기상청 API 키를 넣어주세요.
        self.weather.api_key = '여기에 기상청 api키를 넣거나, .env로부터 api 키를 얻어내세요.'
        
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
