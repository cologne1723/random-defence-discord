import discord
from discord.commands import Option

import dao

async def register_user(ctx: discord.ApplicationContext,
                        user: Option(discord.User, "Discord User"),
                        handle: Option(str, "acmicpc.net ID"),
                        query: Option(str, "solved.ac query")):
    dao.upsertUser(user.id, handle, query.strip())
    embed = discord.Embed(
        title='Updated Data',
        description='',
        color=discord.Colour.dark_red()
    )

    embed.add_field(name='User',value=f'{user}', inline=False)
    embed.add_field(name='acmicpc.net Handle',
                    value=f'{handle} ([solved.ac](https://solved.ac/profile/{handle}), [acmicpc.net](https://www.acmicpc.net/user/{handle}))',
                    inline=False)
    embed.add_field(name='solved.ac Query', value=f'`{query}`', inline=False)

    await ctx.respond("User Register/Update Succeeded!", embed=embed)