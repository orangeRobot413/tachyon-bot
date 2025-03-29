import sys

sys.path.append('./')
from util.config import Config
from util.rcon import rcon

import discord
from discord import app_commands
from discord.ext import commands

import subprocess, signal
import os
from pathlib import Path

from typing import List

# MARK: Read Config
config = Config('config.json')

# MARK: Utilities
signal.signal(signal.SIGCHLD, signal.SIG_IGN)


def start_orphan_server(id: str, server: Config.Server):
    # subprocess.Popen(['screen', '-D', '-R', '-S', id])
    # subprocess.Popen(['screen', '-D', '-S', id])
    subprocess.Popen([
        'screen', '-S', id, '-X', 'stuff',
        f'cd {os.path.join(Path.home(), server.path)}\n'
    ])
    subprocess.Popen([
        'screen', '-S', id, '-X', 'stuff',
        f'java -Xms{server.ram}M -Xmx{server.ram}M {" ".join(server.flags)} ' +
        f'-jar {server.server_jar} --nogui\n'
    ])
    # subprocess.Popen([
    #     'java', f'-Xms{server.ram}M', f'-Xmx{server.ram}M', *server.flags,
    #     '-jar', os.path.join(Path.home(), server.path, server.server_jar), '--nogui'
    # ], close_fds=True, cwd=os.path.join(Path.home(), server.path))

async def kill_server(server: Config.Server):
    await rcon(server.rcon.port, server.rcon.password, "stop")

# MARK: Start Command
start = app_commands.Group(name='start', description='Start Minecraft server(s)')


@start.command(name="all", description='Start all Minecraft servers')
@app_commands.checks.has_role(config.roles.admin)
async def start_all(interaction: discord.Interaction):
    for server in config.servers:
        start_orphan_server(server, config.servers[server])
    embed = discord.Embed(description='Started all servers')
    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed)


@start.command(name="server", description='Start a Minecraft server')
@app_commands.checks.has_role(config.roles.admin)
@app_commands.describe(server='A Minecraft server')
async def start_server(interaction: discord.Interaction, server: str):
    if server in config.servers:
        start_orphan_server(server, config.servers[server])
        embed = discord.Embed(
            description=f'Started {config.servers[server].name}')
        embed.set_footer(text=config.server_name)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description='Server not found')
        embed.set_footer(text=config.server_name)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@start_server.autocomplete('server')
async def _(
        interaction: discord.Interaction,
        current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=choice, value=choice)
        for choice in config.servers
        if current in choice
    ]

# MARK: Stop Command
stop = app_commands.Group(name='stop', description='Stop Minecraft server(s)')


@stop.command(name="all", description='Stop all Minecraft servers')
@app_commands.checks.has_role(config.roles.admin)
async def stop_all(interaction: discord.Interaction):
    for server in config.servers:
        try:
            await kill_server(config.servers[server])
        except ConnectionRefusedError:
            pass
    embed = discord.Embed(description='Stopped all servers')
    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed)


@stop.command(name="server", description='Stop a Minecraft server')
@app_commands.checks.has_role(config.roles.admin)
@app_commands.describe(server='A Minecraft server')
async def stop_server(interaction: discord.Interaction, server: str):
    if server in config.servers:
        try:
            await kill_server(config.servers[server])
            embed = discord.Embed(
                description=f'Stopped {config.servers[server].name}')
            embed.set_footer(text=config.server_name)
            await interaction.response.send_message(embed=embed)
        except ConnectionRefusedError:
            embed = discord.Embed(
                description=f'Server not running')
            embed.set_footer(text=config.server_name)
            await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description='Server not found')
        embed.set_footer(text=config.server_name)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@stop_server.autocomplete('server')
async def _(
        interaction: discord.Interaction,
        current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=choice, value=choice)
        for choice in config.servers
        if current in choice
    ]

# MARK: Setup
async def setup(client: commands.Bot):
    client.tree.add_command(start)
    client.tree.add_command(stop)
