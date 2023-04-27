import datetime

import discord
from discord.ext import tasks
import os  # default module
from dotenv import load_dotenv

from get_random_problem import get_random_problem
from problem_view import ProblemView
from register_user import register_user
from post_daily_prob import post_daily_prob
from post_reminder import post_reminder

import dao


load_dotenv()
intents = discord.Intents.all()
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    bot.add_view(ProblemView())
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name='daily', description='Force Release Daily Problem')
async def daily(ctx: discord.ApplicationContext):
    user = ctx.author
    if 'admin' not in map(lambda x: x.name.lower(), user.roles):
        await ctx.respond("You don't have permission to run command!")
        return
    await post_daily_prob(bot)

@bot.slash_command(name='reminder', description='Force Reminder')
async def reminder(ctx: discord.ApplicationContext):
    user = ctx.author
    if 'admin' not in map(lambda x: x.name.lower(), user.roles):
        await ctx.respond("You don't have permission to run command!")
        return
    await post_reminder(bot)

bot.slash_command(
    name='register', description='Register / Update User Info')(register_user)
bot.slash_command(name='random', description='Select Random Problem!')(
    get_random_problem)


@bot.slash_command(name='list', description='Lists All User')
async def list(ctx: discord.ApplicationContext):
    ret = []
    for did, iid, q in dao.fetchAllUserWithDiscordId():
        u = await bot.fetch_user(did)
        ret.append(f'Discord: `{u}`')
        ret.append(f'acmicpc.net: `{iid}`')
        ret.append(f'query: `{q}`')
        ret.append('')
    await ctx.channel.send(content='\n'.join(ret))


@tasks.loop(time=datetime.time(hour=21, minute=0, second=0, tzinfo=datetime.timezone.utc))
async def daily_post(): await post_daily_prob(bot)

@tasks.loop(time=datetime.time(hour=9, minute=0, second=0, tzinfo=datetime.timezone.utc))
async def daily_reminder(): await post_reminder(bot)

if __name__ == '__main__':
    dao.init()
    daily_post.start()
    bot.run(os.getenv('TOKEN'))  # run the bot with the token
