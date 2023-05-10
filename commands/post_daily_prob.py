import os
import discord

from post_random_problems import post_random_problems


async def post_daily_prob(bot: discord.Bot):
    await bot.wait_until_ready()
    chan = bot\
        .get_guild(int(os.getenv('PROBLEM_GUILD')))\
        .get_channel(int(os.getenv('PROBLEM_CHANNEL')))
    await post_random_problems(chan)
