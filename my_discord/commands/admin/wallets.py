import os
import time

import discord
from discord import app_commands

from base_classes.member import get_member_by_id
from base_classes.mint import is_mint_exist, get_wallets_for_mint
from my_discord.autocomplete import release_id_autocomplete
from my_discord.checkers import admin_checker
from utilities.files import create_wallets_files

__all__ = ["AdminWallets"]


@app_commands.guild_only()
class AdminWallets(app_commands.Group):
    @app_commands.command(name="get-all", description="ADMIN COMMAND Get all wallets for specific release")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_name=release_id_autocomplete)
    @app_commands.describe(release_name="Mint name only from /mints get-all")
    async def get_wallets(self, interaction: discord.Interaction, release_name: str) -> None:
        if not is_mint_exist(mint_name=release_name):
            await interaction.response.send_message(f"There are no releases named as `{release_name}`")
            return
        mint_wallets = get_wallets_for_mint(release_name)
        if not mint_wallets:
            await interaction.response.send_message(f"There are no wallets for `{release_name}`")
            return
        mint_wallets.sort(key=lambda w: w.member_id)
        base_wallets_dir = "wallets_to_send"
        wallets = []
        members_info = {}
        for wallet in mint_wallets:
            if wallet.member_id not in members_info:
                member_name = get_member_by_id(wallet.member_id).name
                members_info[wallet.member_id] = {"name": member_name, "wallets_count": 0}
            member_name = members_info[wallet.member_id]["name"]
            members_info[wallet.member_id]["wallets_count"] += 1
            wallet_number = members_info[wallet.member_id]["wallets_count"]
            wallets.append((f"{member_name}{wallet_number}", wallet.private_key))
        if not os.path.exists(base_wallets_dir):
            os.mkdir(base_wallets_dir)
        timestamp = int(time.time())
        files = {
            "urban": os.path.join(base_wallets_dir, f"{release_name}{timestamp}UR.txt"),
            "pepper": os.path.join(base_wallets_dir, f"{release_name}{timestamp}PP.csv"),
            "minter_suite": os.path.join(base_wallets_dir, f"{release_name}{timestamp}MS.csv")
        }
        create_wallets_files(wallets, files)
        await interaction.response.send_message(files=[discord.File(files[key]) for key in files])
