import os
import time

import discord
from discord import app_commands
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
        print(f'{self.user} has connected to Discord!')


class Drop:
    def __init__(self, name, timestamp=None, link=None):
        self.name = name.strip()
        self.timestamp = timestamp
        self.link = link
        self.wallets = {}

    def get_drop_data(self):
        data = ""
        data += f"**{self.name}** "
        if self.timestamp is not None:
            data += f"<t:{self.timestamp}> "
        if self.link is not None:
            data += f"{self.link.strip()}"
        return data


class ACOMember:
    def __init__(self, member: discord.Member):
        self.member = member
        self.mints = {}


class Mints(app_commands.Group):
    @app_commands.command(name="add", description="Add mint to mints list")
    async def add_mint(self, interaction: discord.Interaction, drop_name: str, link: str = None, timestamp: str = None):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        if any(drop_name.lower().strip() == drop.name.lower() for drop in mints_list):
            await interaction.response.send_message(f"{drop_name} already exist!", ephemeral=True)
        else:
            mints_list.append(Drop(drop_name, timestamp, link))
            await interaction.response.send_message(f"Added `{drop_name}` to drop list!", ephemeral=True)

    @app_commands.command(name="get_all", description="Get actual mints")
    async def get_mints(self, interaction: discord.Interaction):
        data_to_send = ""
        for i, drop in enumerate(mints_list, 1):
            data_to_send += f"{i} {drop.get_drop_data()}\n\n"
        data_to_send += "**Let us know if we lost something. Just use `/mints request_mint` for it!**"
        await interaction.response.send_message(data_to_send)

    @app_commands.command(name="change_info", description="Change mint [name, link or timestamp]")
    async def change_mint_info(self, interaction: discord.Interaction, mint_name: str, change_type: str,
                               new_value: str):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        change_type = change_type.lower().strip()
        new_value = new_value.lower().strip()
        if change_type not in ["name", "link", "timestamp"]:
            await interaction.response.send_message("Invalid change type!", ephemeral=True)
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

    @app_commands.command(name="request_mint", description="Get actual mints")
    async def request_mint(self, interaction: discord.Interaction, drop_name: str, link: str = None,
                           time: str = None):
        admins_to_ping = ""
        for admin_id in config.ADMINS_IDS:
            admins_to_ping += "<@" + str(admin_id) + "> "
        await interaction.response.send_message(
            f"{admins_to_ping}, please add `{drop_name}`, link:`{link}`, time: `{time}`")

    @app_commands.command(name="delete", description="Delete mint from mints list")
    async def delete_mint(self, interaction: discord.Interaction, drop_name: str):
        for i in range(len(mints_list)):
            mint_name = mints_list[i].name
            if drop_name.lower().strip() == mints_list[i].name.lower():
                for file_name in os.listdir("wallets_to_send"):
                    if file_name[:len(mint_name)] == mint_name:
                        os.remove(os.path.join("wallets_to_send", file_name))
                mints_list.pop(i)
                await interaction.response.send_message(f"Deleted `{drop_name}` from drop list!", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"There are no releases named as {drop_name}", ephemeral=True)


class Aco(app_commands.Group):
    @app_commands.command(name="send_wallets", description="Send wallets separeted by commas for chosen release")
    async def send_wallet(self, interaction: discord.Interaction, release_name: str, wallets: str):
        release_name = release_name.strip().lower()
        member_name = interaction.user.name
        if not len(wallets):
            await interaction.response.send_message("Please input wallets keys")
            return

        wallets = [wallet.strip() for wallet in wallets.split(",")]
        for mint in mints_list:
            if mint.name.lower() == release_name:
                if member_name not in mint.wallets:
                    mint.wallets[member_name] = []
                mint.wallets[member_name].extend(wallets)
                await interaction.response.send_message(f"Successfully sent {len(wallets)} wallets")
                return
        else:
            await interaction.response.send_message(f"There are no releases named as {release_name}")

    @app_commands.command(name="get_wallets", description="Get all wallets for specific release")
    async def get_wallets(self, interaction: discord.Interaction, release_name: str):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return

        release_name = release_name.strip().lower()

        if not any(release_name == mint.name.lower() for mint in mints_list):
            await interaction.response.send_message(f"There are no releases named as {release_name}")
            return

        wallets = ""
        for mint in mints_list:
            if mint.name.lower() == release_name:
                for member in mint.wallets:
                    for i, wallet in enumerate(mint.wallets[member], 1):
                        wallets += f"{member.split('#')[0]}{i}:{wallet}\n"

        timestamp = int(time.time())
        file_name = os.path.join("wallets_to_send", f"{release_name}{timestamp}.txt")
        with open(file_name, "w") as file:
            file.write(wallets)
        time.sleep(1)
        await interaction.response.send_message(file=discord.File(file_name))


def check_admin(member_id):
    return member_id in config.ADMINS_IDS


def add_member(member: discord.Member):
    if not any(member.id == aco_member.id for aco_member in aco_members):
        aco_members.append(ACOMember(member))


mints_list = []
aco_members = []
