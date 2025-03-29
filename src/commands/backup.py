import sys

sys.path.append('./')

from util.config import Config
from util.timestamp import timestamp
from util.rcon import rcon

import discord
from discord import app_commands
from discord.ext import commands

import shutil
from datetime import datetime, timezone
import os.path
from pathlib import Path
import re
from typing import List, Optional

config = Config('config.json')


# MARK: Backup Server
async def backup_server(server: Config.Server, filename: Optional[str] = None) -> str:
    print(2)

    archive_path = os.path.join(Path.home(), server.path, 'backups', filename)

    print(server.path)
    print(archive_path)

    try:
        await rcon(server.rcon.port, server.rcon.password, 'say Backing up the server. You may experience some lag...')
        await rcon(server.rcon.port, server.rcon.password, 'save-off')
        await rcon(server.rcon.port, server.rcon.password, 'save-all flush')
    except:
        pass

    shutil.make_archive(archive_path, 'zip', os.path.join(Path.home(), server.path), 'world')

    try:
        await rcon(server.rcon.port, server.rcon.password, 'save-on')
    except:
        pass


# MARK: Command
backup = app_commands.Group(name='backup', description='Backup server(s)')


@backup.command(name='all')
@app_commands.checks.has_role(config.roles.admin)
@app_commands.describe(name='Backup name')
async def _(interaction: discord.Interaction, name: Optional[str]):
    dt = datetime.now(timezone.utc)
    archive_filename = (re.sub(r'\s+', '_', name) + '-'
                        if name is not None else '') + timestamp(dt)

    fail = []

    for server in config.servers:
        try:
            await backup_server(server, archive_filename)
        except:
            fail.append(server)

    if len(fail) > 0:
        embed = discord.Embed(description='Unable to backup:')
        for server in fail:
            embed.description += f'\n**{server}**'
        embed.set_footer(text=config.server_name)
    else:
        embed = discord.Embed(
            description=
            f'Backed up all servers to \"{archive_filename}\".zip files')
        embed.set_footer(text=config.server_name)

    await interaction.response.send_message(embed=embed)


@backup.command()
@app_commands.checks.has_role(config.roles.admin)
@app_commands.describe(server='Minecraft server', name='Backup name')
async def server(interaction: discord.Interaction, server: str,
                 name: Optional[str]):
    if server not in config.servers:
        embed = discord.Embed(description=f'Server not found')
        embed.set_footer(text=config.server_name)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    dt = datetime.now(timezone.utc)
    archive_filename = (re.sub(r'\s+', '_', name) + '-'
                        if name is not None else '') + timestamp(dt)

    try:
        print(1)

        await backup_server(config.servers[server], archive_filename)

        embed = discord.Embed(
            description=f'Backed up {server} to \"{archive_filename}\".zip files')
    except:
        embed = discord.Embed(description=f'Backup failed')

    embed.set_footer(text=config.server_name)

    await interaction.response.send_message(embed=embed)


@server.autocomplete('server')
async def _(
        interaction: discord.Interaction,
        current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=server, value=server)
        for server in config.servers
        if current in server
    ]


# MARK: Setup
async def setup(client: commands.Bot):
    client.tree.add_command(backup)
