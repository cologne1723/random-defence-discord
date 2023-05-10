import asyncio
import datetime

import discord
from discord.ext import tasks
import os  # default module
from dotenv import load_dotenv

from get_random_problem import get_random_problem
from post_user_list import post_user_list
from problem_view import ProblemView
from register_user import register_user
from post_daily_prob import post_daily_prob
from post_reminder import post_reminder
import date_query
from reroll_problem import reroll_problem

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
bot.slash_command(
    name='random', description='Select Random Problem!')(get_random_problem)
bot.slash_command(
    name='list', description='Lists All User')(post_user_list)
bot.slash_command(
    name='reroll', description='Reroll user problem')(reroll_problem)
bot.slash_command(
    name='show_user', description='Show user queries')(date_query.user_query)
bot.slash_command(
    name='clear_date_rule', description='Clear date specific rule')(date_query.clear_date_rule)
bot.slash_command(
    name='add_date_rule', description='Add date specific rule')(date_query.add_date_rule)
bot.slash_command(
    name='clear_day_rule', description='Clear day specific rule')(date_query.clear_day_rule)
bot.slash_command(
    name='add_day_rule', description='Add day specific rule')(date_query.add_day_rule)



@tasks.loop(time=datetime.time(hour=21, minute=0, second=0, tzinfo=datetime.timezone.utc))
async def daily_post(): await post_daily_prob(bot)


@tasks.loop(time=datetime.time(hour=9, minute=0, second=0, tzinfo=datetime.timezone.utc))
async def daily_reminder(): await post_reminder(bot)

async def main():
    dao.init()
    daily_post.start()
    daily_reminder.start()
    await bot.start(os.getenv('TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())

