import discord

from dao import fetchAllUser, postMessage, addProblem
from solved import selectProblemNo
from problem_view import ProblemView


async def post_random_problems(channel: discord.TextChannel):

    message: discord.Message = await channel.send(content="Loading...")
    messagedbid = postMessage(message.id)

    qdict = {}
    users = fetchAllUser()
    for userid, icpcid, query in users:
        if query not in qdict:
            qdict[query] = query
        qdict[query] = qdict[query] + f' -@{icpcid}'

    for k in qdict:
        qdict[k] = selectProblemNo(qdict[k])

    for userid, icpcid, query in sorted(users, key=lambda x: x[1]):
        prob = qdict[query]
        if prob is not None:
            addProblem(messagedbid, userid, prob.problemId, prob.problemName)

    await ProblemView.reloadMessageFromDB(message)
