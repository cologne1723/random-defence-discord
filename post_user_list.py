
import discord
import dao


async def post_user_list(ctx: discord.ApplicationContext):
    await ctx.defer()

    embed = discord.Embed(
        title="User List",
        description='Here is the lists and the queries of users',
        color=discord.Colour.green()
    )

    z = {}

    for did, iid, q in dao.fetchAllUserWithDiscordId():
        u = await ctx.bot.fetch_user(did)
        if q not in z:
            z[q] = []
        z[q].append(f'{u} (`{iid}`)')

    for q in z:
        embed.add_field(name=', '.join(z[q]), value=f'> `{q}`', inline=False)
    await ctx.followup.send(content='', embed=embed)
