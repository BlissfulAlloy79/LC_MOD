import discord
from discord.ext import commands


class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Loaded example.py")

    @commands.slash_command()  # Create a slash command for the supplied guilds.
    async def hello(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="My Amazing Embed",
            description="Embeds are super easy, barely an inconvenience.",
            color=discord.Colour.blurple(),  # Pycord provides a class with default colors you can choose from
        )
        embed.add_field(name="A Normal Field",
                        value="A really nice field with some information. **The description as well as the fields support markdown!**")

        embed.add_field(name="Inline Field 1", value="Inline Field 1", inline=True)
        embed.add_field(name="Inline Field 2", value="Inline Field 2", inline=True)
        embed.add_field(name="Inline Field 3", value="Inline Field 3", inline=True)

        embed.set_footer(text="Footer! No markdown here.")  # footers can have icons too
        embed.set_author(name="Pycord Team", icon_url="https://cdn.discordapp.com/avatars/664857360602365990/2157a16e8430a21a903257ee8fde6f47")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/664857360602365990/2157a16e8430a21a903257ee8fde6f47")
        embed.set_image(url="https://cdn.discordapp.com/avatars/664857360602365990/2157a16e8430a21a903257ee8fde6f47")

        await ctx.respond("Hello! Here's a cool embed.", embed=embed)  # Send the embed with some text


def setup(bot):
    bot.add_cog(Example(bot))
