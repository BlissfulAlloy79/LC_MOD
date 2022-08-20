import discord
import os
import json
import datetime
from main import check_admin_role
from discord import option
from discord.ext import commands

agree_name_list = []
disagree_name_list = []
vote_interaction = []
vote_info = {}
vote_result: str
result_save: dict = {}

agree_msg = """
You have chosen **Agree**!
Please click the button to confirm your choice
***As you are not able to change it later***
"""
disagree_msg = """
You have chosen **Disagree**!
Please click the button to confirm your choice
***As you are not able to change it later***
"""


class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Click to Confirm!", style=discord.ButtonStyle.blurple)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.value = True
        self.stop()

    @discord.ui.button(label="Click to Cancel", style=discord.ButtonStyle.grey)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.value = False
        self.stop()


class VoteModalDoubleChoice(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Voting title(please be clean and short)"))
        self.add_item(discord.ui.InputText(label="Voting description", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        global vote_info, vote_interaction
        vote_interaction.append(interaction)

        embed = discord.Embed(
            title="# voting",
            description=f"vote called by {interaction.user}",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name=self.children[0].value, value=self.children[1].value, inline=False)
        embed.set_footer(text="The vote will last 24 hours since being called")

        vote_info = embed.to_dict()
        await interaction.response.send_message(embeds=[embed], view=VoteChoicesDoubleChoice(message=interaction))


# class VoteModalMultipleChoice(discord.ui.Modal):
#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(*args, **kwargs)
#
#         self.add_item(discord.ui.InputText(
#             label="Voting title(please be clean and short)",
#             style=discord.InputTextStyle.short,
#             placeholder="The Voting Title"
#         ))
#         self.add_item(discord.ui.InputText(
#             label="Voting description",
#             style=discord.InputTextStyle.long,
#             placeholder="the voting description"
#         ))
#         self.add_item(discord.ui.InputText(
#             label="Option count(must be an int >=2 and <=5)",
#             style=discord.InputTextStyle.short,
#             placeholder="2"
#         ))
#         self.add_item(discord.ui.InputText(
#             label="Option description",
#             style=discord.InputTextStyle.long,
#             placeholder="A: option 1\nB: option 2\nC: option 3\n..."
#         ))
#
#     async def callback(self, interaction: discord.Interaction):
#         global vote_interaction, vote_info
#         vote_interaction.append(interaction)
#
#         embed = discord.Embed(
#             title="# voting",
#             description=f"vote called by {interaction.user}",
#             color=discord.Color.dark_gold()
#         )
#         embed.add_field(name=self.children[0].value, value=self.children[1].value, inline=False)
#         embed.add_field(name="Options:", value=self.children[3].value, inline=False)
#         embed.set_footer(text="The vote will last 24 hours since being called")
#
#         vote_info = embed.to_dict()
#         await interaction.response.send_message(embed=[embed])


class VoteChoicesDoubleChoice(discord.ui.View):
    def __init__(self, message):
        super().__init__(timeout=None)
        self.message = message

    async def end_vote(self):
        global vote_interaction, vote_info, agree_name_list, disagree_name_list, vote_result
        self.agree.label = f"Agree: {len(agree_name_list)}"
        self.disagree.label = f"Disagree: {len(disagree_name_list)}"
        self.agree.disabled = True
        self.disagree.disabled = True
        await self.message.edit_original_message(view=self)
        await self.message.followup.send("The voting ends")
        vote_interaction.clear()
        # await self.message.followup.send(str(vote_info))

    async def inventory_vote_results(self):
        global vote_interaction, vote_info, agree_name_list, disagree_name_list, vote_result, result_save
        if len(agree_name_list) == len(disagree_name_list):
            vote_result = "Tie"
        elif len(agree_name_list) > len(disagree_name_list):
            vote_result = "Passed"
        elif len(agree_name_list) < len(disagree_name_list):
            vote_result = "Not Passed"

        embed = discord.Embed(
            title="# voting results",
            description=f"result of the vote called by {self.message.user}",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name=vote_info["fields"][0]["name"], value=vote_info["fields"][0]["value"], inline=False)
        embed.add_field(name="Agree Count: ", value=str(len(agree_name_list)), inline=True)
        embed.add_field(name="Disagree Count: ", value=str(len(disagree_name_list)), inline=True)
        embed.add_field(name="Voting Result: ", value=vote_result, inline=False)

        embed.set_footer(
            text=f"Total of {len(agree_name_list) + len(disagree_name_list)} member(s) participated in the vote"
        )

        result_save = embed.to_dict()
        result_save["timestamp"] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        await self.message.followup.send("Processing results...", embed=embed)

        with open('.\\config\\vote\\vote_records.json', 'r', encoding='utf-8') as r:
            vote_record = json.load(r)
        vote_record.append(result_save)
        with open('.\\config\\vote\\vote_records.json', 'w', encoding='utf-8') as w:
            json.dump(vote_record, w, indent=4)

    @discord.ui.button(label="Agree: 0", style=discord.ButtonStyle.green, custom_id="agree")
    async def agree(self, button: discord.ui.Button, interaction: discord.Interaction):
        global agree_name_list, disagree_name_list
        view = Confirm()
        if str(interaction.user) not in agree_name_list + disagree_name_list:
            await interaction.response.send_message(agree_msg, ephemeral=True, view=view)
            await view.wait()
            if view.value is True:
                if vote_interaction and str(interaction.user) not in agree_name_list + disagree_name_list:
                    agree_name_list.append(str(interaction.user))
                    button.label = f"Agree: {len(agree_name_list)}"
                    await self.message.edit_original_message(view=self)
                    await interaction.followup.send("You have confirmed your choice on **Agree**!", ephemeral=True)
                elif str(interaction.user) in agree_name_list:
                    await interaction.followup.send("You have made the choice already", ephemeral=True)
                elif str(interaction.user) in disagree_name_list:
                    await interaction.followup.send("You have chosen disagree, don't change side", ephemeral=True)
                elif not vote_interaction:
                    await interaction.followup.send("The vote has ended!", ephemeral=True)

            elif view.value is False:
                await interaction.followup.send("Cancelled confirmation...", ephemeral=True)

        elif str(interaction.user) in agree_name_list:
            await interaction.response.send_message("You have made the choice already", ephemeral=True)

        elif str(interaction.user) in disagree_name_list:
            await interaction.response.send_message("You have chosen disagree, don't change side", ephemeral=True)

    @discord.ui.button(label="Disagree: 0", style=discord.ButtonStyle.red, custom_id="disagree")
    async def disagree(self, button: discord.ui.Button, interaction: discord.Interaction):
        global agree_name_list, disagree_name_list
        view = Confirm()
        if str(interaction.user) not in agree_name_list + disagree_name_list:
            await interaction.response.send_message(disagree_msg, ephemeral=True, view=view)
            await view.wait()
            if view.value is True:
                if vote_interaction and str(interaction.user) not in agree_name_list + disagree_name_list:
                    disagree_name_list.append(str(interaction.user))
                    button.label = f"Disagree: {len(disagree_name_list)}"
                    await self.message.edit_original_message(view=self)
                    await interaction.followup.send("You have confirmed your choice on **Disagree**!", ephemeral=True)
                elif str(interaction.user) in disagree_name_list:
                    await interaction.followup.send("You have made the choice already", ephemeral=True)
                elif str(interaction.user) in agree_name_list:
                    await interaction.followup.send("You have chosen agree, don't change side", ephemeral=True)
                elif not vote_interaction:
                    await interaction.followup.send("The vote has ended!", ephemeral=True)

            elif view.value is False:
                await interaction.followup.send("Cancelled confirmation...", ephemeral=True)

        elif str(interaction.user) in disagree_name_list:
            await interaction.response.send_message("You have made the choice already", ephemeral=True)

        elif str(interaction.user) in agree_name_list:
            await interaction.response.send_message("You have chosen agree, don't change side", ephemeral=True)


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Loaded vote.py")
        if not os.path.exists('.\\config\\vote'):
            os.makedirs('.\\config\\vote')
        if not os.path.exists('.\\config\\vote\\vote_records.json'):
            with open('.\\config\\vote\\vote_records.json', 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)

    @commands.slash_command(
        name="vote",
        description="call a vote"
    )
    @option(
        "vote_type",
        str,
        description="choose the vote type",
        choices=["Double(Agree/Disagree)", "Multiple(Multiple Choice)"]
    )
    async def vote(
            self,
            ctx: discord.ApplicationContext,
            vote_type: str
    ):
        global vote_interaction, agree_name_list, disagree_name_list
        print(f"{ctx.author} executed /vote in {ctx.channel}")
        if check_admin_role(ctx):
            if vote_interaction:
                await ctx.respond(f"There is a ongoing vote, please end it before calling another one")
            else:
                if vote_type == "Double(Agree/Disagree)":
                    agree_name_list.clear()
                    disagree_name_list.clear()
                    modal = VoteModalDoubleChoice(title="Double Choice Voting")
                    await ctx.send_modal(modal)
                elif vote_type == "Multiple(Multiple Choice)":
                    await ctx.respond("this type is not supported yet")
        else:
            await ctx.respond(f"{ctx.author.mention}, you don't have the permission!")

    @commands.slash_command(
        name="vote-end",
        description="ends the vote"
    )
    async def vote_end(
            self,
            ctx: discord.ApplicationContext,
    ):
        global vote_interaction
        print(f"{ctx.author} executed /vote-end in {ctx.channel}")
        if check_admin_role(ctx):
            if vote_interaction:
                await ctx.respond("Ending vote...")
                await VoteChoicesDoubleChoice(message=vote_interaction[0]).inventory_vote_results()
                await VoteChoicesDoubleChoice(message=vote_interaction[0]).end_vote()
            elif not vote_interaction:
                await ctx.respond("There is no ongoing vote")
        else:
            await ctx.respond(f"{ctx.author.mention}, you don't have the permission!")


# def setup(bot):
#     bot.add_cog(Vote(bot))

# Remarks:
# voting inventory done
# vote confirmation done
#
# how to end vote, (manual/auto?)
# still some parts haven't been finished
# Multiple vote function
