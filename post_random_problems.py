import datetime
import discord
import pytz

from dao import fetchAllQueriesForDate, postMessage, addProblem
from solved import selectProblemNo
from problem_view import ProblemView


async def post_random_problems(channel: discord.TextChannel):

    message: discord.Message = await channel.send(content="Loading...")
    messagedbid = postMessage(message.id)

    nd = (datetime.datetime.now(pytz.UTC) + datetime.timedelta(hours=3, minutes=1)).date()
    qdict = {}
    users = fetchAllQueriesForDate(nd)
    for userid, icpcid, query in users:
        if query not in qdict:
            qdict[query] = query
        if query != '-':
            qdict[query] = qdict[query] + f' -@{icpcid}'

    for k in qdict:
        if k != '-':
            qdict[k] = await selectProblemNo(qdict[k])
        else:
            qdict[k] = None

    for userid, icpcid, query in sorted(users, key=lambda x: x[1]):
        prob = qdict[query]
        if prob is not None:
            addProblem(messagedbid, userid, prob.problemId, prob.problemName)
    await ProblemView.reloadMessageFromDB(message)
