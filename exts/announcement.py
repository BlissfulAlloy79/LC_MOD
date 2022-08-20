import discord
import datetime
from main import check_admin_role
from discord import option
from discord.ext import commands


class Announcement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Loaded announcement.py")

    @commands.slash_command(
        name="announcement",
        description="make an announcement"
    )
    @option("announce_desc", str, description="the description", required=True)
    @option("sub_head_1", str, description="first sub-heading", required=True)
    @option("content_1", str, description="first content", required=True)
    @option("inline_1", bool, description="first section inline", default=False)
    @option("sub_head_2", str, description="second sub-heading", default=None)
    @option("content_2", str, description="second content", default=None)
    @option("inline_2", bool, description="second section inline", default=False)
    @option("image_url", str, description="insert image url", default=None)
    async def announcement(
            self,
            ctx: discord.ApplicationContext,
            announce_desc: str,
            sub_head_1: str,
            content_1: str,
            inline_1: bool,
            sub_head_2: str,
            content_2: str,
            inline_2: bool,
            image_url: str
    ):
        print(f"{ctx.author} executed /announcement in {ctx.channel}")
        if check_admin_role(ctx):
            embed = discord.Embed(
                title="# announcement",
                description=announce_desc,
                color=discord.Colour.blurple()
            )

            embed.add_field(name=sub_head_1, value=content_1, inline=inline_1)
            if sub_head_2:
                embed.add_field(name=sub_head_2, value=content_2, inline=inline_2)
            if image_url:
                embed.set_image(url=image_url)

            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar.url}")
            embed.set_footer(text=f"{datetime.datetime.now().strftime('%d/%m/%Y %I%p')}")

            await ctx.respond(f"Processing...")
            await ctx.send(embed=embed)
        else:
            await ctx.respond(f"{ctx.author.mention}, you don't have the permission!")


def setup(bot):
    bot.add_cog(Announcement(bot))

# this function needs improvement
