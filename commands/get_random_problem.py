import discord
from discord.commands import Option

from api.solved import selectRandomProblem

async def getRandomProblem(ctx: discord.ApplicationContext,
                             query: Option(str, "Random Problem Query")):

    randomProblem = await selectRandomProblem(query)
    embed = discord.Embed(
        title='Random Problem Query',
        description='Here is a Problem For You!',
        color=discord.Colour.blurple()
    )
    embed.add_field(name='Query', value=f'`{query}`', inline=False)
    if randomProblem is not None:
        embed.add_field(name='Chosen Problem', value=randomProblem.problemMarkDown(), inline=False)
    else:
        embed.add_field(name='Result', value='No problem found.', inline=False)

    await ctx.respond("", embed=embed)