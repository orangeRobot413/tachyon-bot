import discord
from discord import app_commands
from discord.ext import commands

from typing import List, Optional
import json

from util.filesize import *

# MARK: Read Config
file = open('config.json')
data = json.load(file)
server_name=data['server_name']
servers = data['servers']
file.close()


# MARK: Command
@app_commands.command(description='Get size of worlds')
@app_commands.describe(server='A Minecraft server')
async def worldsize(interaction: discord.Interaction, server: Optional[str]):
    if server is None:
        embed = discord.Embed(title='World Sizes', description='')
        for server in servers:
            embed.description += f'**{servers[server]['name']}:** {format_file_size(get_file_size(servers[server]['path']))}\n'
        embed.set_footer(text=server_name)
        await interaction.response.send_message(embed=embed)
        return

    if server not in servers:
        await interaction.response.send_message('Sever not found',
                                                ephemeral=True)
        return

    embed = discord.Embed(title=servers[server]['name'], description=format_file_size(get_file_size(servers[server]['path'])))
    embed.set_footer(text=server_name)
    await interaction.response.send_message(embed=embed)
    return


@worldsize.autocomplete('server')
async def _(
        interaction: discord.Interaction,
        current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=choice, value=choice)
        for choice in servers
        if current in choice
    ]


# MARK: Setup
async def setup(client: commands.Bot):
    client.tree.add_command(worldsize)
