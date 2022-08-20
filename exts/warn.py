import discord
import json
import os
from main import check_admin_role
from exts.timeout import timeout_member
from discord import option
from discord.ext import commands

warn_record_format = {
    "warnList": [],
    "timeoutRecord": {}
}

warn_record_path = ".\\config\\warn\\warn_records.json"


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Loaded warn.py")
        if not os.path.exists('.\\config\\warn'):
            os.makedirs('.\\config\\warn')
        if not os.path.exists(warn_record_path):
            with open(warn_record_path, 'w', encoding='utf-8') as f:
                json.dump(warn_record_format, f, indent=4)

    @commands.slash_command(
        name="warn",
        description="warn a member"
    )
    @option(
        "member",
        discord.Member,
        description="choose a member",
        required=True
    )
    async def warn(
            self,
            ctx: discord.ApplicationContext,
            member: discord.Member
    ):
        print(f"{ctx.author} executed /warn in #{ctx.channel}")
        if check_admin_role(ctx):
            await ctx.respond(f"warning `{member}`")

            with open(warn_record_path, 'r', encoding='utf-8') as r:
                records = json.load(r)

            warn_list = records["warnList"]
            timeout_record = records["timeoutRecord"]

            if str(member) not in warn_list:
                warn_list.append(str(member))
                await ctx.send(f"{member.mention}, you have received a warning!")
                await ctx.send(f"next warning will result penalty")
            elif str(member) in warn_list:
                warn_list.remove(str(member))
                if str(member) in timeout_record:
                    timeout_record[str(member)] += 1
                elif str(member) not in timeout_record:
                    timeout_record[str(member)] = 1
                await ctx.send(f"{member.mention}, you've been warned again!")
                await ctx.send(f"resulting penalty...")
                await timeout_member(
                    ctx=ctx,
                    member=member,
                    minutes=timeout_record[str(member)]**2,
                    reason="achieved warning penalty"
                )

            records["warnList"] = warn_list
            records["timeoutRecord"] = timeout_record

            with open(warn_record_path, 'w', encoding='utf-8') as w:
                json.dump(records, w, indent=4)
        else:
            await ctx.respond(f"{ctx.author.mention}, you don't have the permission!")


def setup(bot):
    bot.add_cog(Warn(bot))
