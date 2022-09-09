import discord
from discord.ext import commands

import config


class DiscordClient(commands.Bot):
    def __init__(self, prefix="!"):
        super().__init__(intents=discord.Intents.all(), command_prefix=prefix)
        self.synced = False

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        print(f'{client.user} has connected to Discord!')


class Drop:
    def __init__(self, name, timestamp, link):
        self.name = name
        self.timestamp = timestamp
        self.link = link

    def get_drop_data(self):
        data = ""
        data += f"**{self.name}** "
        if self.timestamp is not None:
            data += f"<t:{self.timestamp}> "
        if self.link is not None:
            data += f"{self.link}"
        return data


mints_list = []

client = DiscordClient(config.PREFIX)


@client.tree.command(name="add_drop", description="Add mint to mints list")
async def add_mint(interaction: discord.Interaction, drop_name: str, link: str = None, timestamp: int = None):
    if any(drop_name.lower().strip() == drop.name for drop in mints_list):
        await interaction.response.send_message(f"{drop_name} already exist!")
    else:
        mints_list.append(Drop(drop_name, link, timestamp))
        await interaction.response.send_message(f"Added {drop_name} to drop list!")


@client.tree.command(name="get_drops", description="Get actual mints")
async def get_mints(interaction: discord.Interaction):
    data_to_send = ""
    for drop in mints_list:
        data_to_send += drop.get_drop_data()
    if data_to_send:
        await interaction.response.send_message(data_to_send)
    else:
        await interaction.response.send_message("Where are no drops")


client.run(config.TOKEN)
