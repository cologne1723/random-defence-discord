from commands.clear_query import clearQuery
from commands.set_query import setQuery
from commands.set_channel import setChannel
from commands.register_user import registerUser
from commands.get_random_problem import getRandomProblem
from commands.show_user import showUser
from db.base import DB
import asyncio
import datetime

import discord
from discord.ext import tasks
import os  # default module
from dotenv import load_dotenv
load_dotenv()


intents = discord.Intents.all()
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


bot.slash_command(name='random',
                  description='Select Random Problem!')(getRandomProblem)
bot.slash_command(name='register',
                  description='Register / Modify User Information')(registerUser)
bot.slash_command(name='show_user',
                  description='Show User Info')(showUser)
bot.slash_command(name='set_query',
                  description='Make Your Own Query')(setQuery)
bot.slash_command(name='meta_set_channel',
                  description='Set Channel Usage')(setChannel)
bot.slash_command(name='clear_query',
                  description='Delete Your Own query')(clearQuery)


async def main():
    await DB.connect()
    await bot.start(os.getenv('TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
