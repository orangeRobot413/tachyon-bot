import discord
from discord import app_commands
from discord.ext import commands

from typing import Optional
import json

# MARK: Read Config
file = open('config.json')
data = json.load(file)
server_name = data['server_name']
file.close()



# MARK: Command
@app_commands.command(description='Bans a user')
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(user='User or User ID')
async def ban(interaction: discord.Interaction, user: discord.User,
                reason: Optional[str]):
    global_name = user.global_name
    user_id = user.id

    await interaction.guild.ban(user=user)

    embed = discord.Embed(description=f'Banned {global_name} ({user_id})')
    embed.set_footer(text=server_name)
    await interaction.response.send_message(embed=embed)


# MARK: Setup
async def setup(client: commands.Bot):
    client.tree.add_command(ban)
