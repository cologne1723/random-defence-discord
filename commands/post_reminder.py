import os
import discord

from remind_unsolved import remind_unsolved


async def post_reminder(bot: discord.Bot):
    await bot.wait_until_ready()
    chan = bot\
        .get_guild(int(os.getenv('PROBLEM_GUILD')))\
        .get_channel(int(os.getenv('REMINDER_CHANNEL')))
    await remind_unsolved(chan)
