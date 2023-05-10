import discord
from discord.commands import Option

from api.solved import selectProblemNo

async def get_random_problem(ctx: discord.ApplicationContext,
                             query: Option(str, "Random Problem Query")):

    pno = await selectProblemNo(query)
    embed = discord.Embed(
        title='Random Problem Query',
        description='Here is a Problem For You!',
        color=discord.Colour.blurple()
    )

    embed.add_field(name='Query', value=f'`{query}`', inline=False)

    if pno is not None:
        embed.add_field(name='Chosen Problem',
                        value=f'[**{pno.problemId}** {pno.problemName}]({pno.problemLink()})',
                        inline=False)
    else:
        embed.add_field(name='Result', value='No problem found.', inline=False)

    await ctx.respond("", embed=embed)