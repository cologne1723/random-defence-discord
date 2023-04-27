import datetime
import discord
from dao import loadSolvedStatusFromDiscordMessageId, MakeUnsolvedProblemPending, getPendingProblems, updateSolvedStatus, setSolvedStatus
from solved import checklistsolved


class ProblemView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout of the view must be set to None

    @staticmethod
    async def reloadMessageFromDB(message=discord.Message):
        embed = discord.Embed(
            title="Today's Random Problem",
            description='Here is a Problem For You!',
            color=discord.Colour.green()
        )
        statuses = loadSolvedStatusFromDiscordMessageId(message.id)
        for icpcid, problemid, problemname, solved in statuses:
            solved_emoji = [':white_large_square:', ':white_check_mark:',
                            ':arrows_counterclockwise:', ':sleeping_accommodation:'][solved]
            embed.add_field(name=icpcid,
                            value=f'{solved_emoji} [**{problemid}** {problemname}](https://acmicpc.net/problem/{problemid})',
                            inline=False)
        await message.edit(content='', embed=embed, view=ProblemView())

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
        r = checklistsolved(k)

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
