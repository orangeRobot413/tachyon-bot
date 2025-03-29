import sys

sys.path.append('./')
from util.config import Config

import discord
from discord import app_commands
import discord.context_managers
from discord.ext import commands

from dotenv import dotenv_values
from typing import List, Optional
import os

# MARK: Config
config = Config('config.json')

# MARK: Setup
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!!', intents=intents)


# MARK: Extensions
async def load_commands():
    filenames = [
        filename for filename in os.listdir('./src/commands')
        if os.path.isfile(f'./src/commands/{filename}') and filename.endswith('.py')
    ]

    print(f'\x1b[1mLoading {len(filenames)} extension(s):\x1b[0m')

    for filename in filenames:
        try:
            await client.load_extension(f'commands.{filename[:-3]}')
            print(filename)
        except Exception as error:
            print(f'\x1b[31m\x1b[9m{filename}\x1b[0m')
            print(f'\x1b[31m{error}\x1b[0m')


async def sync_commands():
    try:
        synced = await client.tree.sync()
        print(f'\x1b[1mSynced {len(synced)} command(s):\x1b[0m')
        for command in synced:
            print(command)
    except Exception as e:
        print(e)


# MARK: Help


def command_name_list(l: List[app_commands.Command],
                      only_subcommands=True) -> List[str]:
    names = []
    for command in l:
        if isinstance(command, app_commands.Group):
            if not only_subcommands:
                names += [command.name]
            names += [
                command.name + ' ' + subcommand
                for subcommand in command_name_list(command.commands)
            ]
        else:
            names += [command.name]
    return names


def get_command_from_name(tree: app_commands.CommandTree[commands.Bot] |
                          app_commands.Group, name: List[str]):
    if len(name) == 1:
        return tree.get_command(name[0])
    else:
        return get_command_from_name(tree.get_command(name[0]), name[1:])


@client.tree.command(description='Displays help for commands')
@app_commands.rename(command_name='command')
async def help(interaction: discord.Interaction, command_name: Optional[str]):

    if command_name is not None:
        try:
            command = get_command_from_name(client.tree, command_name.split())
            embed = discord.Embed(title=command.name,
                                  description=command.description)
        except:
            embed = discord.Embed(description='Command not found')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    else:
        embed = discord.Embed(
            title='Commands',
            description='Use `/help [command]` for more info on a command\n')

        embed.description += '\n' + '\n'.join(
            command_name_list(client.tree.get_commands()))

    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed)


@help.autocomplete('command_name')
async def _(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=name, value=name)
        for name in command_name_list(client.tree.get_commands(), False)
        if current in name
    ]


# MARK: Ping
@client.tree.command(description='Responds with the bots current latency')
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        description=f'Pong! {round(1000 * client.latency)} ms')
    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed)


# MARK: Reload
reload = app_commands.Group(name='reload',
                            description='Reload the bot or its extensions')


@reload.command(description='Reloads the bot')
@app_commands.checks.has_role(config.roles.admin)
async def bot(interaction: discord.Interaction):
    embed = discord.Embed(
        description='Killing bot. Will restart momentarily...')
    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed)

    await client.close()


@reload.command(
    name='commands',
    description='Reloads the bot\'s commands without reloading the bot')
@app_commands.checks.has_role(config.roles.admin)
async def _(interaction: discord.Interaction):
    embed = discord.Embed(description='Loading commands...')
    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed)

    filenames = [
        filename for filename in os.listdir('./commands')
        if os.path.isfile(f'./commands/{filename}') and filename.endswith('.py')
    ]

    print(f'\x1b[1mReloading {len(filenames)} extension(s):\x1b[0m')

    for filename in filenames:
        try:
            await client.reload_extension(f'commands.{filename[:-3]}')
            print(filename)
        except:
            print(f'\x1b[31m\x1b[9m{filename}\x1b[0m')

    msg = await interaction.original_response()

    embed.description = 'Syncing commands...'
    await msg.edit(embed=embed)

    await sync_commands()

    embed.description = 'Finished reloading commands'
    await msg.edit(embed=embed)


client.tree.add_command(reload)

# MARK: Set Status
setstatus = app_commands.Group(name='setstatus',
                               description='Set/reset bot\'s status')


@setstatus.command(description='Set bot\'s status')
@app_commands.checks.has_role(config.roles.admin)
@app_commands.describe(message='Status message')
async def message(interaction: discord.Interaction, message: str):
    await client.change_presence(activity=discord.CustomActivity(name=message))

    embed = discord.Embed(description=f'Set status to \"{message}\"')
    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed)


@setstatus.command(
    description=f'Reset status to \"Playing {config.server_name}\"')
@app_commands.checks.has_role(config.roles.admin)
async def default(interaction: discord.Interaction):
    await client.change_presence(activity=discord.Game(name=config.server_name))

    embed = discord.Embed(
        description=f'Reset status to \"Playing {config.server_name}\"')
    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed)


client.tree.add_command(setstatus)


# MARK: On Command Error
@client.tree.error
async def _(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandNotFound):
        msg = 'Command not found'
    elif isinstance(error, app_commands.MissingPermissions) or isinstance(
            error, app_commands.MissingRole):
        msg = 'Insufficient permissions'
    else:
        raise error

    embed = discord.Embed(description=msg)
    embed.set_footer(text=config.server_name)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# MARK: On Ready
@client.event
async def on_ready():
    print(f'\x1b[1mLogged in as {client.user}\x1b[0m')

    await load_commands()
    await sync_commands()

    # Suppress default help command
    client.help_command = None

    # Presecence

    await client.change_presence(activity=discord.Game(name=config.server_name))


# MARK: Main
def main():
    client.run(config.discord_token)


if __name__ == '__main__':
    main()
