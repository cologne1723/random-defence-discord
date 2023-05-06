import datetime
import discord
from dao import loadSolvedStatusFromDiscordMessageId, MakeUnsolvedProblemPending, getPendingProblems, updateSolvedStatus, setSolvedStatus
from solved import checklistsolved


class ProblemView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout of the view must be set to None

    @staticmethod
    async def reloadMessageFromDB(message=discord.Message):
        
        
        def new_embed(first: bool):
            e = discord.Embed(
                title="Today's Random Problem" if first else '',
                description='Here is a Problem For You!' if first else '',
                color=discord.Colour.green(),
            )
            return e
        
        statuses = loadSolvedStatusFromDiscordMessageId(message.id)
        cnt = 0

        embeds = []
        embed = new_embed(True)
        for icpcid, problemid, problemname, solved, rolled in statuses:
            solved_emoji = [':white_large_square:', ':white_check_mark:',
                            ':arrows_counterclockwise:', ':sleeping_accommodation:'][solved]
            rolled_emoji = ['', ':game_die:'][rolled]
            problem_link = f'[**{problemid}** {problemname}](https://acmicpc.net/problem/{problemid})'
            embed.add_field(name=icpcid,
                            value=f'{solved_emoji} {problem_link} {rolled_emoji}',
                            inline=True)
            cnt += 1
            if cnt % 3 == 2:
               cnt += 1
               embed.add_field(name='\u200b', value='\u200b', inline=True)
            if cnt >= 24:
                cnt = 0
                embeds.append(embed)
                embed = new_embed(False)
        if cnt != 0:
            embeds.append(embed)
        await message.edit(content='', embeds=embeds, view=ProblemView())

    @staticmethod
    async def check_expire(message: discord.Message):
        if datetime.datetime.now(tz=datetime.timezone.utc) < message.created_at + datetime.timedelta(days=1):
            return False
        v = discord.ui.View.from_message(message)
        for child in v.children:
            child.disabled = True
        await message.edit(view=v)
        return True

    @discord.ui.button(
        label="Check Solve",
        custom_id="solvedac-reload-button",
        style=discord.ButtonStyle.primary,
        emoji='✅')  # the button has a custom_id set
    async def check_solve(self, button: discord.Button, interaction: discord.Interaction):
        if (await ProblemView.check_expire(interaction.message)):
            await interaction.response.defer()
            return

        await interaction.response.defer()
        setSolvedStatus(interaction.message.id, interaction.user.id, 2)
        MakeUnsolvedProblemPending(interaction.message.id)
        await ProblemView.reloadMessageFromDB(interaction.message)

        pendings = getPendingProblems(interaction.message.id)

        k = []
        for dbid, icpcid, problemid in pendings:
            k.append((problemid, icpcid))
        r = await checklistsolved(k)

        for dbid, icpcid, problemid in pendings:
            solved = 1 if r[(problemid, icpcid)] else 0
            updateSolvedStatus(dbid, solved)

        await ProblemView.reloadMessageFromDB(interaction.message)

    @discord.ui.button(
        label="Skip Problem",
        custom_id="solvedac-skip-button",
        style=discord.ButtonStyle.secondary,
        emoji='🛌')  # the button has a custom_id set
    async def skip_problem(self, button: discord.Button, interaction: discord.Interaction):
        if (await ProblemView.check_expire(interaction.message)):
            await interaction.response.defer()
            return
        await interaction.response.defer()
        setSolvedStatus(interaction.message.id, interaction.user.id, 3)
        await ProblemView.reloadMessageFromDB(interaction.message)
