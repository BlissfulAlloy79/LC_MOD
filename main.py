import json
import os
import discord

config_default = {
  "token": None,
  "guildID": None,
  "commandChannel": None,
  "announcementChannel": None,
  "monitoringChannels": [],
  "adminRoleID": None,
  "SchemPath": None
}

if not os.path.exists('.\\config'):
    os.makedirs('.\\config')
if not os.path.exists('config.json'):
    with open('config.json', 'w', encoding='utf-8') as j:
        json.dump(config_default, j, indent=4)
    print("Please fill in the config!")
    exit()

with open(r'config.json', encoding='utf-8') as f:
    cfg = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(intents=intents, debug_guilds=[cfg["guildID"]])


def check_admin_role(ctx: discord.ApplicationContext):
    if ctx.author.get_role(cfg["adminRoleID"]) is None:
        return False
    elif ctx.author.get_role(cfg["adminRoleID"]):
        return True


@bot.event
async def on_ready():
    print(f"Bot has logged in as {bot.user} (ID: {bot.user.id})")
    print("-----")


@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.system_channel is not None:
        msg = f"Welcome {member.mention} to {member.guild.name}"
        await member.guild.system_channel.send(msg)


@bot.event
async def on_member_remove(member: discord.Member):
    if member.guild.system_channel is not None:
        msg = f"Bye {member.mention}"
        await member.guild.system_channel.send(msg)


@bot.event
async def on_message_delete(message: discord.Message):
    if message.channel.id in cfg["monitoringChannels"]:
        msg = f"`{message.author}'s message was deleted`"
        await message.channel.send(msg)


@bot.slash_command()
async def test(ctx: discord.ApplicationContext):
    if check_admin_role(ctx):
        await ctx.respond(f"You have the role")
    else:
        await ctx.respond(f"You don't have the role")

# noinspection SpellCheckingInspection
for extension in os.listdir('./exts'):
    if extension.endswith('.py'):
        # noinspection SpellCheckingInspection
        bot.load_extension(f'exts.{extension[:-3]}')

if __name__ == "__main__":
    bot.run(cfg["token"])
