import os
import discord

from dao import getUnsolvedOrPendingUsers, getLastMessageId


async def remind_unsolved(channel: discord.TextChannel):
    messageid = int(getLastMessageId())
    users = getUnsolvedOrPendingUsers(messageid)
    guild = os.getenv('PROBLEM_GUILD')
    channelid = os.getenv('PROBLEM_CHANNEL')
    url =  f'https://discord.com/channels/{guild}/{channelid}/{messageid}'
    mentions = ' '.join(f'<@{user[0]}>' for user in users)
    await channel.send(f'''{mentions}
문제 풀고 :white_check_mark:를 눌러주세요
휴가 사용은 :sleeping_accommodation:를 눌러주세요
{url}''')