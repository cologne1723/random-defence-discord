import discord
from discord.commands import Option
from db.base import DB

from helper.check_user import isAdmin


async def clearQuery(ctx: discord.ApplicationContext,
                   rank: Option(str, "Order of rule to remove."),
                   user: Option(discord.User, "Discord User", required=False),
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
    existingRule = await DB.queryrule.find_first(where={'queryRuleRank': rank, 'userId': dbUser.id})
    if existingRule is None:
        await ctx.respond(f'Rule with rank `{rank}` does not exist.')
        return

    await DB.queryrule.delete(where={'id': existingRule.id})
    await ctx.respond(f'Destroyed rule with rank `{rank}`.')
