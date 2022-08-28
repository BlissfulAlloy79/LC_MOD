import discord
import os
import json
import datetime
from main import check_admin_role
from discord import option
from discord.ext import commands

blacklist = []
agree_name_list = []
disagree_name_list = []
vote_embed = {}
vote_status = 0  # 0: no ongoing vote, 1: vote ongoing
vote_message: discord.Message  # store the vote message for edit
result: dict  # store the vote result as dict to send

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


class DoubleChoiceModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Double Choice Voting")

        self.add_item(discord.ui.InputText(label="Voting title(please be clean and short)"))
        self.add_item(discord.ui.InputText(label="Voting description", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        global vote_status, agree_name_list, disagree_name_list, vote_embed
        vote_status = 1

        embed = discord.Embed(
            title="# voting",
            description=f"vote called by {interaction.user}",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name=self.children[0].value, value=self.children[1].value, inline=False)
        embed.add_field(name="Agree:", value=f"{len(agree_name_list)}", inline=True)
        embed.add_field(name="Disagree:", value=f"{len(disagree_name_list)}", inline=True)
        embed.set_footer(text="The vote should last 24 hours since being called")

        vote_embed = embed.to_dict()
        print(f"{vote_embed}")
        await interaction.response.send_message("Processing...")
        self.stop()


# noinspection SpellCheckingInspection
async def inventory_doublechoice_results():
    global agree_name_list, disagree_name_list, vote_embed, result, vote_message
    color = discord.Color.gold()
    vote_result = "Failed"
    if len(agree_name_list) == len(disagree_name_list):
        vote_result = "Tie"
        color = discord.Color.light_gray()
    elif len(agree_name_list) > len(disagree_name_list):
        vote_result = "Passed"
        color = discord.Color.green()
    elif len(agree_name_list) < len(disagree_name_list):
        vote_result = "Not Passed"
        color = discord.Color.red()

    embed = discord.Embed(
        title="# voting results",
        description=f"result of the {vote_embed['description']}",
        colour=color
    )
    embed.add_field(name=vote_embed["fields"][0]["name"], value=vote_embed["fields"][0]["value"], inline=False)
    embed.add_field(name="Agree Count: ", value=str(len(agree_name_list)), inline=True)
    embed.add_field(name="Disagree Count: ", value=str(len(disagree_name_list)), inline=True)
    embed.add_field(name="Voting Result: ", value=vote_result, inline=False)

    embed.set_footer(
        text=f"Total of {len(agree_name_list) + len(disagree_name_list)} member(s) participated in the vote"
    )

    result = embed.to_dict()
    result["timestamp"] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    with open('.\\config\\vote\\vote_records.json', 'r', encoding='utf-8') as r:
        vote_record = json.load(r)
        vote_record.append(result)
    with open('.\\config\\vote\\vote_records.json', 'w', encoding='utf-8') as w:
        json.dump(vote_record, w, indent=4)

    await vote_message.reply("Vote has ended, inventorying results...", embeds=[embed])


class DoubleChoiceButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=86400)

    async def end_vote(self):
        global vote_status, vote_message, vote_embed
        vote_embed["title"] = "# ended-vote"
        edit_embed = discord.Embed.from_dict(vote_embed)
        await vote_message.edit(embeds=[edit_embed], view=DoubleChoiceDummyButton())
        await inventory_doublechoice_results()
        vote_status = 0
        self.stop()

    async def cancel_vote(self):
        global vote_status, vote_message, vote_embed
        vote_embed["title"] = "# cancelled-vote"
        edit_embed = discord.Embed.from_dict(vote_embed)
        await vote_message.edit(embeds=[edit_embed], view=DoubleChoiceDummyButton())
        await vote_message.reply("Vote was cancelled")
        vote_status = 0
        self.stop()

    @discord.ui.button(label="Agree", style=discord.ButtonStyle.green)
    async def agree(self, button: discord.ui.Button, interaction: discord.Interaction):
        global agree_name_list, disagree_name_list, vote_message, vote_status, blacklist
        if vote_status == 1:
            view = Confirm()
            await interaction.response.send_message(agree_msg, view=view, ephemeral=True)
            await view.wait()
            if view.value:
                if vote_status == 0:
                    await interaction.followup.send("Vote has ended!", ephemeral=True)
                elif str(interaction.user) in agree_name_list + disagree_name_list:
                    await interaction.followup.send("You have voted already!", ephemeral=True)
                elif str(interaction.user) in blacklist:
                    await interaction.followup.send("Invalid Confirmation", ephemeral=True)
                else:
                    agree_name_list.append(str(interaction.user))
                    vote_embed["fields"][1]["value"] = f"{len(agree_name_list)}"
                    embed = discord.Embed.from_dict(vote_embed)
                    await interaction.followup.edit_message(vote_message.id, embeds=[embed])
                    await interaction.followup.send("You have confirmed your choice on **Agree**!", ephemeral=True)
            elif view.value is False:
                await interaction.followup.send("Cancelled confirmation...", ephemeral=True)
        else:
            await interaction.response.send_message("There is no vote going on", ephemeral=True)

    @discord.ui.button(label="Disagree", style=discord.ButtonStyle.red)
    async def disagree(self, button: discord.ui.Button, interaction: discord.Interaction):
        global agree_name_list, disagree_name_list, vote_message, vote_status, blacklist
        if vote_status == 1:
            view = Confirm()
            await interaction.response.send_message(disagree_msg, view=view, ephemeral=True)
            await view.wait()
            if view.value:
                if vote_status == 0:
                    await interaction.followup.send("Vote has ended!", ephemeral=True)
                elif str(interaction.user) in agree_name_list + disagree_name_list:
                    await interaction.followup.send("You have voted already!", ephemeral=True)
                elif str(interaction.user) in blacklist:
                    await interaction.followup.send("Invalid confirmation", ephemeral=True)
                else:
                    disagree_name_list.append(str(interaction.user))
                    vote_embed["fields"][2]["value"] = f"{len(disagree_name_list)}"
                    embed = discord.Embed.from_dict(vote_embed)
                    await interaction.followup.edit_message(vote_message.id, embeds=[embed])
                    await interaction.followup.send("You have confirmed your choice on **Disagree**", ephemeral=True)
            elif view.value is False:
                await interaction.followup.send("Cancelled confirmation...", ephemeral=True)
        else:
            await interaction.response.send_message("There is no vote going on", ephemeral=True)


class DoubleChoiceDummyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=3)

    @discord.ui.button(label="Agree", style=discord.ButtonStyle.green, disabled=True)
    async def agree(self):
        pass

    @discord.ui.button(label="Disagree", style=discord.ButtonStyle.red, disabled=True)
    async def disagree(self):
        pass


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Loaded vote.py")
        if not os.path.exists('.\\config\\vote'):
            os.makedirs('.\\config\\vote')
        if not os.path.exists('.\\config\\vote\\vote_records.json'):
            with open('.\\config\\vote\\vote_records.json', 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
        if not os.path.exists('.\\config\\vote\\vote_blacklist.json'):
            with open('.\\config\\vote\\vote_blacklist.json', 'w', encoding='utf-8') as b:
                json.dump([], b, indent=4)

    @commands.slash_command(name="vote", description="call a vote")
    @option(
        "vote_type",
        str,
        description="choose the voting type",
        choices=["Double(Agree/Disagree)", "Multiple(Multiple Choice)"]
    )
    async def vote(self, ctx: discord.ApplicationContext, vote_type: str):
        global vote_message, vote_embed, agree_name_list, disagree_name_list, blacklist
        print(f"{ctx.author} executed /vote in {ctx.channel}")
        with open('.\\config\\vote\\vote_blacklist.json', 'r', encoding='utf-8') as r:
            blacklist = json.load(r)
        if check_admin_role(ctx):
            if vote_status == 0:
                if vote_type == "Double(Agree/Disagree)":
                    agree_name_list.clear()
                    disagree_name_list.clear()
                    modal = DoubleChoiceModal()
                    await ctx.send_modal(modal)
                    await modal.wait()
                    embed = discord.Embed.from_dict(vote_embed)
                    # print(vote_embed)
                    message = await ctx.send("Vote:", embeds=[embed], view=DoubleChoiceButton())
                    vote_message = message
                    # await ctx.send(str(message.id))
                elif vote_type == "Multiple(Multiple Choice)":
                    await ctx.respond("This is not supported yet", ephemeral=True)
            elif vote_status == 1:
                await ctx.respond("There is a ongoing vote")
        else:
            await ctx.respond(f"{ctx.author.mention}, you don't have permission!")

    @commands.slash_command(name="vote-end", description="Ends an ongoing vote")
    async def vote_end(self, ctx: discord.ApplicationContext):
        global vote_status, agree_name_list, disagree_name_list
        print(f"{ctx.user} executed /vote-end in {ctx.channel}")
        if check_admin_role(ctx):
            if vote_status == 0:
                await ctx.respond("There is no ongoing vote")
            elif vote_status == 1:
                await ctx.respond("Processing...")
                await DoubleChoiceButton().end_vote()
                vote_status = 0
        else:
            await ctx.respond(f"{ctx.author.mention}, you don't have permission!")

    @commands.slash_command(name="vote-blacklist", description="Voting blacklist")
    @option("method", str, description="Choose type", choices=["add", "remove", "list"], required=True)
    @option("member", discord.Member, description="choose a member", required=False)
    async def vote_blacklist(self, ctx: discord.ApplicationContext, method: str, member: discord.Member):
        global blacklist
        print(f"{ctx.user} executed /vote-blacklist in {ctx.channel}")
        if check_admin_role(ctx):
            with open('.\\config\\vote\\vote_blacklist.json', 'r', encoding='utf-8') as r:
                blacklist = json.load(r)
            if method == "list":
                msg = '\n'.join(blacklist)
                await ctx.respond(f"```\n{msg}\n```")
            elif method == "add":
                if member is None:
                    await ctx.respond("You did not enter the member!")
                elif str(member) in blacklist:
                    await ctx.respond("Member already exists!")
                else:
                    blacklist.append(str(member))
                    with open('.\\config\\vote\\vote_blacklist.json', 'w', encoding='utf-8') as w:
                        json.dump(blacklist, w, indent=4)
                    await ctx.respond(f"Added `{member}` into the blacklist")
            elif method == "remove":
                if member is None:
                    await ctx.respond("You did not enter the member!")
                elif str(member) not in blacklist:
                    await ctx.respond(f"`{member}` is not in the blacklist")
                else:
                    blacklist.remove(str(member))
                    with open('.\\config\\vote\\vote_blacklist.json', 'w', encoding='utf-8') as w:
                        json.dump(blacklist, w, indent=4)
                    await ctx.respond(f"Removed `{member}` from blacklist")
        else:
            await ctx.respond(f"{ctx.author.mention}, you don't have permission!")

    @commands.slash_command(name="vote-cancel", description="Cancel a ongoing vote")
    async def vote_cancel(self, ctx: discord.ApplicationContext):
        global vote_status
        print(f"{ctx.user} executed /vote-cancel in {ctx.channel}")
        if check_admin_role(ctx) is False:
            await ctx.respond(f"{ctx.author.mention}, you don't have permission!")
        elif check_admin_role(ctx):
            if vote_status == 0:
                await ctx.respond("There is no ongoing vote")
            elif vote_status == 1:
                await ctx.respond("Cancelling vote...")
                await DoubleChoiceButton().cancel_vote()


def setup(bot):
    bot.add_cog(Vote(bot))

# vote multiple choice
