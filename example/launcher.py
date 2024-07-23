from bot_example import Test
import asyncio
import discord
import os

async def main():
    async with Test() as bot:
        discord.utils.setup_logging()
        await bot.start(os.getenv('discord_token'))


if __name__ == "__main__":
    asyncio.run(main())