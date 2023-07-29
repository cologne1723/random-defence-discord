import discord
from discord.commands import Option
from db.base import DB
from helper.make_embed import makeEmbedsFromDBUser


async def showUser(ctx: discord.ApplicationContext,
                   user: Option(discord.User, "Discord User"),
                   verbose: Option(bool, required=False),
                   ):
    if user is None:
        user = ctx.author
    result = await DB.user.find_first(where={'discordId': str(user.id)}, include={'QueryRule': {
        'order_by': {'queryRuleRank': 'asc'}
    }})
    if result is None:
        await ctx.respond("User is not registered...", ephemeral=True)
        return

    embeds = await makeEmbedsFromDBUser(ctx.bot, result, verbose=verbose)
    await ctx.respond("User Data", embeds=embeds)
