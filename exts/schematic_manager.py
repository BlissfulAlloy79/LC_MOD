import discord
import json
import os
from main import cfg
from discord import option
from discord.ext import commands

schematic_list = []


async def get_schematics(ctx):
    return [schematics for schematics in os.listdir(cfg["SchemPath"])]


class SchemUpload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Loaded schematic_manager.py")

    @commands.slash_command(
        name="schem-list",
        description="list cmp schematic files"
    )
    async def schem_list(
            self,
            ctx: discord.ApplicationContext
    ):
        print(f"{ctx.author} executed /schem-list in {ctx.channel}")
        list_msg = '\n'.join(os.listdir(cfg["SchemPath"]))
        await ctx.respond(f"```\n{list_msg}\n```")

    @commands.slash_command(
        name="schem-upload",
        description="upload file"
    )
    @option(
        "file_upload",
        discord.Attachment,
        description="choose the schematic file to upload",
        required=True
    )
    async def schem_upload(
            self,
            ctx: discord.ApplicationContext,
            file_upload: discord.Attachment
    ):
        print(f"{ctx.author} executed /schem-upload in {ctx.channel}")
        await ctx.respond(f"uploading file: `{file_upload.filename}")
        file_name = file_upload.filename.split('.')
        if len(file_name) == 2 and file_name[1] == 'schem':
            if file_upload.filename in os.listdir(cfg["SchemPath"]):
                await ctx.send(f"`{file_upload.filename}` already exists!")
                await ctx.send("Please use another name")
            else:
                save_loc = cfg["SchemPath"] + f'\\{file_upload.filename}'
                await file_upload.save(save_loc)
                await ctx.send(f"`{file_upload.filename}` uploaded successfully!")
        else:
            await ctx.send("file error!")
            await ctx.send("please check if the file is correct")

    @commands.slash_command(
        name="schem-download",
        description="download cmp schematic files"
    )
    @option(
        "download_file",
        str,
        description="choose file you want to download",
        required=True,
        autocomplete=get_schematics
    )
    async def schem_download(
            self,
            ctx: discord.ApplicationContext,
            download_file: str
    ):
        print(f"{ctx.author} executed /schem-download in {ctx.channel}")
        file_loc = cfg["SchemPath"] + f'\\{download_file}'
        await ctx.respond(file=discord.File(file_loc))

    @commands.slash_command(
        name="schem-remove",
        description="remove a cmp schematic file"
    )
    @option(
        "remove_file",
        str,
        description="choose file you want to remove",
        required=True,
        autocomplete=get_schematics
    )
    async def schem_remove(
            self,
            ctx: discord.ApplicationContext,
            remove_file: str
    ):
        print(f"{ctx.author} executed /schem-remove in {ctx.channel}")
        await ctx.respond(f"removing file: {remove_file}")
        file_path = cfg["SchemPath"] + f'\\{remove_file}'
        if os.path.exists(file_path):
            os.remove(file_path)
            await ctx.send(f"successfully removed `{remove_file}`")
        else:
            await ctx.send("An error occurred!")
            await ctx.send(f"file: `{remove_file}` does not exist!")

    @commands.Cog.listener()
    async def on_application_command_error(
            self,
            ctx: discord.ApplicationContext,
            error: discord.DiscordException
    ):
        print(str(error))
        raise error


def setup(bot):
    bot.add_cog(SchemUpload(bot))
