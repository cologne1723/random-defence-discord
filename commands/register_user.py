import discord
from discord.commands import Option
from db.base import DB
from helper.check_user import isAdmin
from helper.make_embed import makeEmbedsFromDBUser

async def registerUser(ctx: discord.ApplicationContext,
                       user: Option(discord.User, "Discord User", required=False),
                       handle: Option(str, "solved.ac ID", required=False),
                       reminderat: Option(int, "Reminder Timing (Default: 18)", min_value=0, max_value=23, required=False)):

    if user is None:
        user = ctx.author
    if user != ctx.author and not isAdmin(ctx.author):
        await ctx.respond("You don't have permission to run command!", ephemeral=True)
        return
    if handle is None and reminderat is None:
        await ctx.respond("Specify at least one of `handle` or `reminderat`.", ephemeral=True)
        return


    data = {'discordId': str(user.id)}
    if handle is not None:
        data['solvedId'] = handle
    if reminderat is not None:
        data['reminderAt'] = reminderat

    result = await DB.user.find_first(where={'discordId': str(user.id)})
    if result is None:
        if handle is None:
            await ctx.respond("`handle` required for new user registration.", ephemeral=True)
            return
        result = await DB.user.create(data=data)
    else:
        result = await DB.user.update(data=data, where={'id': result.id})

    embeds = await makeEmbedsFromDBUser(ctx.bot, result)
    await ctx.respond("User Register/Update Succeeded!", embeds=embeds)