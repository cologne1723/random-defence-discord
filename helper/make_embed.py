
import discord
from db.base import DB
from prisma.models import QueryRule, User

from helper.date_tool import nowAsISO


async def makeEmbedsFromDBUser(bot: discord.Bot, user: User, description='', verbose=False):

    embeds = []

    # make default embed
    embed = discord.Embed(
        title='User Data',
        description=description,
        color=discord.Colour.green()
    )

    discorduser = await bot.get_or_fetch_user(user.discordId)
    handle = user.solvedId

    embed.add_field(name='User', value=f'{discorduser}', inline=False)
    embed.add_field(name='solved.ac Handle',
                    value=f'{handle} ([solved.ac](https://solved.ac/profile/{handle}), [acmicpc.net](https://www.acmicpc.net/user/{handle}))',
                    inline=False)
    embed.add_field(name='Reminder At',
                    value=f'`{user.reminderAt}:00`', inline=False)
    embeds.append(embed)

    if user.QueryRule is not None:
        for qr in user.QueryRule:
            em = makeEmbedFromQueryRule(qr, verbose=verbose)
            if em is not None:
                embeds.append(em)

    return embeds


def makeEmbedFromQueryRule(queryRule: QueryRule, description='', verbose=False):

    embed = discord.Embed(
        title='Query',
        description=description,
        color=discord.Colour.blue()
    )

    embed.add_field(
        name='Query', value=f'`{queryRule.solvedacQuery}`', inline=False)
    if not queryRule.overwrite:
        embed.add_field(name='Overwrite',
                        value='Do not overwrite', inline=False)
    elif verbose:
        embed.add_field(name='Overwrite', value='Overwrite', inline=False)

    if verbose or (queryRule.endDate is None) or (queryRule.endDate >= nowAsISO()):
        if queryRule.startDate is not None or verbose:
            embed.add_field(name='Start Date', value=str(queryRule.startDate))
        if queryRule.endDate is not None or verbose:
            embed.add_field(name='End Date', value=str(queryRule.startDate))
    if not verbose and queryRule.endDate is not None and queryRule.endDate < nowAsISO():
        return None

    dayRules = []
    if queryRule.onSunday:
        dayRules.append('Sun')
    if queryRule.onMonday:
        dayRules.append('Mon')
    if queryRule.onTuesday:
        dayRules.append('Tue')
    if queryRule.onWednesday:
        dayRules.append('Wed')
    if queryRule.onThursday:
        dayRules.append('Thu')
    if queryRule.onFriday:
        dayRules.append('Fri')
    if queryRule.onSaturday:
        dayRules.append('Sat')

    if len(dayRules) != 7 or verbose:
        embed.add_field(name='Days', value=', '.join(dayRules), inline=False)

    if queryRule.probability < 1.0 or verbose:
        embed.add_field(name='Probability', value=str(queryRule.probability))

    if verbose:
        embed.add_field(name='Rule Index',
                        value=f'`{queryRule.queryRuleRank}`')

    return embed
