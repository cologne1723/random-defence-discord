import os
import discord
from discord import Option, User
from problem_view import ProblemView
import solved

from dao import getLastMessageId, getQueryOfUser, setLastDefenceProblem
from typing import Optional

class RerollView(discord.ui.View):
    def __init__(self, qs:str, req_user: User, user: User, prob: Optional[solved.ICPCProblem], msg: discord.Message):
        super().__init__(timeout=20)  # timeout of the view must be set to None
        self.reroll_req_user = req_user
        self.reroll_user = user
        self.reroll_prob = prob
        embed = discord.Embed(
            title="Reroll Info",
            description='Reroll using follow information:',
            color=discord.Colour.red()
        )
        self.msg = msg
        self.reroll_disabled = False


        embed.add_field(name='User', value=f'`{user}`', inline=False)
        embed.add_field(name='Query', value=f'`{qs}`', inline=False)

        if prob is not None:
            embed.add_field(name='Chosen Problem',
                            value=f'[**{prob.problemId}** {prob.problemName}]({prob.problemLink()})',
                            inline=False)
        else:
            embed.add_field(name='Result', value='No problem found.', inline=False)
            for child in self.children:
                child.disabled = True
        
        self.reroll_embed = embed

    async def on_timeout(self):
        if self.reroll_disabled:
            return
        for child in self.children:
            child.disabled = True
        await self.message.edit(content=":x: Reroll canceled (timeout)", view=self)

    @discord.ui.button(
        label="Change Problem",
        style=discord.ButtonStyle.danger)
    async def change_prob(self, button:discord.Button, interaction : discord.Interaction):
        if interaction.user != self.reroll_req_user:
            return
        self.reroll_disabled = True
        for child in self.children:
            child.disabled = True
        await interaction.response.defer()
        await self.message.edit(content=":white_check_mark: Reroll Confirmed!", view=self)
        setLastDefenceProblem(
            self.reroll_user.id,
            self.reroll_prob.problemId,
            f'{self.reroll_prob.problemName}',
            1
        )
        await ProblemView.reloadMessageFromDB(self.msg)

    
    @discord.ui.button(
        label="Cancel Reroll",
        style=discord.ButtonStyle.secondary)
    async def cancel_reroll(self, button, interaction):
        if interaction.user != self.reroll_req_user:
            return
        self.reroll_disabled = True
        for child in self.children:
            child.disabled = True
        await interaction.response.defer()
        await self.message.edit(content=":x: Reroll canceled (user)", view=self)



async def reroll_problem(ctx: discord.ApplicationContext,
                             user: Option(User, "Discord User"),
                             query: Option(str, "Random Problem Query", required=False)):



    request_user = ctx.author
    if request_user != user and 'admin' not in map(lambda x: x.name.lower(), request_user.roles):
        await ctx.respond("> You don't have permission to run command!")
        return

    if query is None:
        iq = getQueryOfUser(user.id)
        if iq is None:
            await ctx.respond(f"> {user} doesn't have Random Defence Query!")
            return

        icpcid, query = iq
        query += f' -@{icpcid}'

    prob = await solved.selectProblemNo(query)
    messageid = int(getLastMessageId())
    chan = await ctx.bot.fetch_channel(os.getenv('PROBLEM_CHANNEL'))
    msg = await chan.fetch_message(messageid)
    view = RerollView(query, ctx.user, user, prob, msg)
    await ctx.respond(view=view, embed=view.reroll_embed)
