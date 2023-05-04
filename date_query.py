import discord
from discord.commands import Option
import dao
import datetime
import pytz


async def user_query(ctx: discord.ApplicationContext,
                     user: Option(discord.User, "Discord User")):
    res = dao.getQueryOfUser(user.id)
    if res is None:
        await ctx.respond("User is not registered")
        return
    handle, qry = res
    embed = discord.Embed(
        title=f'Data of User {user}',
        description='',
        color=discord.Colour.blue()
    )

    embed.add_field(name='acmicpc.net Handle',
                    value=f'{handle} ([solved.ac](https://solved.ac/profile/{handle}), [acmicpc.net](https://www.acmicpc.net/user/{handle}))',
                    inline=False)
    embed.add_field(name='Default Query', value=f'> `{qry}`', inline=False)


    dq = dao.fetchAllDateQueryFrom(
        user.id,
        (datetime.datetime.now(pytz.UTC) + datetime.timedelta(hours=3)).date())
    for sd, ed, qr in dq:
        embed.add_field(name=f'{sd} ~ {ed}', value=f'> `{qr}`', inline=False)

    dq = dao.fetchAllDayQuery(user.id)
    for d, qr in dq:
        dn = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][d]
        embed.add_field(name=f'{dn}', value=f'> `{qr}`', inline=False)

    await ctx.respond("", embed=embed)


async def clear_day_rule(ctx: discord.ApplicationContext,
                       user: Option(discord.User, "Discord User"),
                       day: Option(str, "Choose day of week",
                                   choices=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                                            'Weekday', 'Weekend'])):

    request_user = ctx.author
    if request_user != user and 'admin' not in map(lambda x: x.name.lower(), request_user.roles):
        await ctx.respond("You don't have permission to run command!")
        return

    dbid = dao.getDbIdOfUser(user.id)
    if dbid is None:
        await ctx.respond("User is not registered")
        return

    daylist = {
        'Monday': [0],
        'Tuesday': [1],
        'Wednesday': [2],
        'Thursday': [3],
        'Friday': [4],
        'Saturday': [5],
        'Sunday': [6],
        'Weekday': [0, 1, 2, 3, 4],
        'Weekend': [5, 6]
    }[day]

    for d in daylist:
        dao.removeDayQuery(dbid, d)


    embed = discord.Embed(
        title='Removed Day-Specific Data',
        description='',
        color=discord.Colour.dark_red()
    )

    embed.add_field(name='User', value=f'{user}', inline=False)
    embed.add_field(name='Day', value=f'{day}', inline=True)

    await ctx.respond("Day Data Update Succeeded!", embed=embed)

async def clear_date_rule(ctx: discord.ApplicationContext,
                          user: Option(discord.User, "Discord User"),
                          start_date: Option(str, "Discord User"),
                          end_date: Option(str, "acmicpc.net ID")):

    request_user = ctx.author
    if request_user != user and 'admin' not in map(lambda x: x.name.lower(), request_user.roles):
        await ctx.respond("You don't have permission to run command!")
        return

    if start_date > end_date:
        await ctx.respond("Make Sure startDate <= endDate")
        return

    try:
        SDD = datetime.date.fromisoformat(start_date)
        EDD = datetime.date.fromisoformat(end_date)
    except ValueError:
        await ctx.respond("Make Sure Dates have format YYYY-MM-DD")
        return

    dbid = dao.getDbIdOfUser(user.id)
    if dbid is None:
        await ctx.respond("User is not registered")
        return

    dao.RemoveDateRangeQuery(dbid, SDD, EDD)
    embed = discord.Embed(
        title='Removed Date-Specific Data',
        description='',
        color=discord.Colour.dark_red()
    )

    embed.add_field(name='User', value=f'{user}', inline=False)
    embed.add_field(name='From', value=f'{start_date}', inline=True)
    embed.add_field(name='To', value=f'{end_date}', inline=True)

    await ctx.respond("Date Data Remove Succeeded!", embed=embed)

async def add_day_rule(ctx: discord.ApplicationContext,
                       user: Option(discord.User, "Discord User"),
                       day: Option(str, "Choose day of week",
                                   choices=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                                            'Weekday', 'Weekend']),
                        query: Option(str, "solved.ac query")):

    request_user = ctx.author
    if request_user != user and 'admin' not in map(lambda x: x.name.lower(), request_user.roles):
        await ctx.respond("You don't have permission to run command!")
        return

    dbid = dao.getDbIdOfUser(user.id)
    if dbid is None:
        await ctx.respond("User is not registered")
        return

    daylist = {
        'Monday': [0],
        'Tuesday': [1],
        'Wednesday': [2],
        'Thursday': [3],
        'Friday': [4],
        'Saturday': [5],
        'Sunday': [6],
        'Weekday': [0, 1, 2, 3, 4],
        'Weekend': [5, 6]
    }[day]

    for d in daylist:
        dao.removeDayQuery(dbid, d)
        dao.addDayQuery(dbid, d, query)

    embed = discord.Embed(
        title='Updated Data',
        description='',
        color=discord.Colour.dark_red()
    )

    embed.add_field(name='User', value=f'{user}', inline=False)
    embed.add_field(name='Day', value=f'{day}', inline=True)
    embed.add_field(name='solved.ac Query', value=f'`{query}`', inline=False)

    await ctx.respond("Day Data Update Succeeded!", embed=embed)


async def add_date_rule(ctx: discord.ApplicationContext,
                        user: Option(discord.User, "Discord User"),
                        start_date: Option(str, "Discord User"),
                        end_date: Option(str, "acmicpc.net ID"),
                        query: Option(str, "solved.ac query")):

    request_user = ctx.author
    if request_user != user and 'admin' not in map(lambda x: x.name.lower(), request_user.roles):
        await ctx.respond("You don't have permission to run command!")
        return

    if start_date > end_date:
        await ctx.respond("Make Sure startDate <= endDate")
        return

    try:
        SDD = datetime.date.fromisoformat(start_date)
        EDD = datetime.date.fromisoformat(end_date)
    except ValueError:
        await ctx.respond("Make Sure Dates have format YYYY-MM-DD")
        return

    dbid = dao.getDbIdOfUser(user.id)
    if dbid is None:
        await ctx.respond("User is not registered")
        return

    dao.RemoveDateRangeQuery(dbid, SDD, EDD)
    dao.addDateQuery(dbid, SDD, EDD, query)
    embed = discord.Embed(
        title='Updated Data',
        description='',
        color=discord.Colour.dark_red()
    )

    embed.add_field(name='User', value=f'{user}', inline=False)
    embed.add_field(name='From', value=f'{start_date}', inline=True)
    embed.add_field(name='To', value=f'{end_date}', inline=True)
    embed.add_field(name='solved.ac Query', value=f'`{query}`', inline=False)

    await ctx.respond("Date Data Update Succeeded!", embed=embed)
