import datetime
import discord
from discord.commands import Option
from db.base import DB

from helper.check_user import isAdmin
from helper.make_embed import makeEmbedFromQueryRule


async def setQuery(ctx: discord.ApplicationContext,
                   query: Option(str, "Random Problem Query (`-` for empty)"),
                   user: Option(discord.User, "Discord User", required=False),
                   start: Option(str, "YYYY-MM-DD format date of start (incl)", required=False),
                   end: Option(str, "YYYY-MM-DD format date of end (incl)", required=False),
                   day: Option(str, "Comma-separated list of Sun/Mon/Tue/Wed/Thu/Fri/Sat to work", required=False),
                   prob: Option(float, "Probability of queryRule to work", required=False),
                   rank: Option(str, "Order of rule to execute. (Lexicographic, defaulting by appending `i` on last)", required=False),
                   overwrite: Option(
                       bool, "Whether to overwrite previous rule (default: true)", required=False)
                   ):

    if user is None:
        user = ctx.author
    if user != ctx.author and not isAdmin(ctx.author):
        await ctx.respond("You don't have permission to run command!", ephemeral=True)
        return

    dbUser = await DB.user.find_first(where={'discordId': str(user.id)}, include={
        'QueryRule': {
            'order_by': {
                'queryRuleRank': 'asc',
            }
        }
    })
    if dbUser is None:
        await ctx.respond("User is not registered.", ephemeral=True)
        return

    if start is not None and end is not None and start > end:
        await ctx.respond("Make Sure startDate <= endDate")
        return

    try:
        if start is not None:
            datetime.date.fromisoformat(start)
        if end is not None:
            datetime.date.fromisoformat(end)
    except ValueError:
        await ctx.respond("Make Sure Dates have format YYYY-MM-DD")
        return

    data = {'overwrite': overwrite is None or overwrite == True,
            'onSunday': day is None or 'sun' in day.lower(),
            'onMonday': day is None or 'mon' in day.lower(),
            'onTuesday': day is None or 'tue' in day.lower(),
            'onWednesday': day is None or 'wed' in day.lower(),
            'onThursday': day is None or 'thu' in day.lower(),
            'onFriday': day is None or 'fri' in day.lower(),
            'onSaturday': day is None or 'sat' in day.lower(),
            'probability': 1 if prob is None else prob,
            'userId': dbUser.id,
            }

    if not (data['onSunday'] or data['onMonday'] or data['onTuesday'] or data['onWednesday'] or data['onThursday'] or data['onFriday'] or data['onSaturday']):
        await ctx.respond("Specify one day at least")
        return

    if start is not None:
        data['startDate'] = start
    if end is not None:
        data['endDate'] = end

    if rank is None:
        existingRule = await DB.queryrule.find_first(where=data)
    else:
        existingRule = await DB.queryrule.find_first(where={'queryRuleRank': rank, 'userId': dbUser.id})
    if existingRule is not None:
        updatedRule = await DB.queryrule.update({'solvedacQuery': query}, where={'id': existingRule.id})
        await ctx.respond('', embed=makeEmbedFromQueryRule(
            updatedRule, f'Updated query for `{user}`', verbose=True))
        return

    if rank is None:
        if dbUser.QueryRule:
            rank = dbUser.QueryRule[-1].queryRuleRank + 'i'
        else:
            rank = 'i'

    data['queryRuleRank'] = rank
    data['solvedacQuery'] = query
    createdQueryRule = await DB.queryrule.create(data=data)

    await ctx.respond('', embed=makeEmbedFromQueryRule(
        createdQueryRule, f'Created query for `{user}`', verbose=True))
