import discord
from discord import app_commands
from discord.ext import commands


class DiscordClient(commands.Bot):
    def __init__(self, prefix="!"):
        super().__init__(intents=discord.Intents.all(), command_prefix=prefix)
        self.synced = False

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        print(f'{self.user} has connected to Discord!')


class Drop:
    def __init__(self, name, timestamp, link):
        self.name = name.strip()
        self.timestamp = timestamp
        self.link = link

    def get_drop_data(self):
        data = ""
        data += f"**{self.name}** "
        if self.timestamp is not None:
            data += f"<t:{self.timestamp}> "
        if self.link is not None:
            data += f"{self.link.strip()}"
        return data


class Mints(app_commands.Group):

    @app_commands.command(name="add", description="Add mint to mints list")
    async def add_mint(self, interaction: discord.Interaction, drop_name: str, link: str = None, timestamp: str = None):
        if any(drop_name.lower().strip() == drop.name.lower() for drop in mints_list):
            await interaction.response.send_message(f"{drop_name} already exist!")
        else:
            mints_list.append(Drop(drop_name, timestamp, link))
            await interaction.response.send_message(f"Added {drop_name} to drop list!", ephemeral=True)

    @app_commands.command(name="get_all", description="Get actual mints")
    async def get_mints(self, interaction: discord.Interaction):
        data_to_send = ""
        for drop in mints_list:
            data_to_send += drop.get_drop_data()
        if data_to_send:
            await interaction.response.send_message(data_to_send)
        else:
            await interaction.response.send_message("Where are no drops:(")

    @app_commands.command(name="change_info", description="Change mint [name, link or timestamp]")
    async def change_mint_info(self, interaction: discord.Interaction, mint_name: str, change_type: str,
                               new_value: str):
        change_type = change_type.lower().strip()
        new_value = new_value.lower().strip()
        if change_type not in ["name", "link", "timestamp"]:
            await interaction.response.send_message("Invalid change type!")
            return
        for mint in mints_list:
            if mint.name.lower() == mint_name.lower().strip():
                if change_type == "name":
                    mint.name = new_value
                if change_type == "link":
                    mint.link = new_value
                if change_type == "timestamp":
                    mint.timestamp = new_value
                await interaction.response.send_message(f"Successfully changed {change_type} to {new_value}",
                                                        ephemeral=True)
                return


mints_list = []
