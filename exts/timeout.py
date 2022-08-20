import discord
import datetime
from main import check_admin_role
from discord import option
from discord.ext import commands


async def timeout_member(ctx: discord.ApplicationContext, member: discord.Member, minutes: int, reason: str):
    duration = datetime.timedelta(minutes=minutes)
    try:
        await member.timeout_for(duration=duration, reason=reason)
        await ctx.send(f"timing out `{member}` for `{duration}`")
        if reason:
            await ctx.send(f"reason: `{reason}`")
    except Exception as e:
        await ctx.send("An error occurred")
        print(str(e))
        await ctx.send(f"`{str(e)}`")


class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Loaded timeout.py")

    @commands.slash_command(
        name="timeout",
        description="warn a member"
    )
    @option(
        "member",
        discord.Member,
        required=True
    )
    @option(
        "minutes",
        int,
        required=True
    )
    @option(
        "reason",
        str,
        required=False,
        default=None
    )
    async def timeout(
            self,
            ctx: discord.ApplicationContext,
            member: discord.Member,
            minutes: int,
            reason: str
    ):
        print(f"{ctx.author} executed /timeout in {ctx.channel}")
        if check_admin_role(ctx):
            await ctx.respond("processing timeout")
            await timeout_member(ctx, member, minutes, reason)
        else:
            await ctx.respond(f"{ctx.author.mention}, you don't have the permission!")


def setup(bot):
    bot.add_cog(Timeout(bot))
