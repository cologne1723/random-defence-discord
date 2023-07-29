import discord
from discord.commands import Option

from api.solved import selectRandomProblem
from db.base import DB
from helper.check_user import isAdmin

async def setChannel(ctx: discord.ApplicationContext,
                           name: Option(str, "Channel purpose", choices = ['Daily', 'Weekly', 'Reminder', 'Log']),
                           channel: Option(discord.TextChannel, "Chosen Channel")):

    if not isAdmin(ctx.author):
        await ctx.respond("You don't have permission to run command!", ephemeral=True)
        return


    result = await DB.channel.find_first(where={'channelName': name})
    data = {'channelName': name, 'channelId': str(channel.id)}
    if result is None:
        result = await DB.channel.create(data=data)
    else:
        result = await DB.channel.update(data=data, where={'id': result.id})

    embed = discord.Embed(
        title='Channel Modification',
        description='Channel Successfully Modified.',
        color=discord.Colour.red()
    )
    embed.add_field(name='Purpose', value=f'`{name}`', inline=False)
    embed.add_field(name='Channel', value=channel.mention, inline=False)

    await ctx.respond("", embed=embed)