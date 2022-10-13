import os
import time

import discord
from discord import app_commands

from additions.autocomplete import release_id_autocomplete
from additions.checkers import admin_checker
from functions.files import create_wallets_files
from functions.members import get_member_name_by_id
from functions.mints import get_mint_by_id


@app_commands.guild_only()
class AdminWallets(app_commands.Group):
    @app_commands.command(name="get-all", description="ADMIN COMMAND Get all wallets for specific release")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_id=release_id_autocomplete)
    @app_commands.describe(release_id="Mint name only from /mints get-all")
    async def get_wallets(self, interaction: discord.Interaction, release_id: str):
        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as `{release_id}`")
            return
        if all(not mint.wallets[member_id] for member_id in mint.wallets):
            await interaction.response.send_message(f"There are no wallets for `{release_id}`")
            return
        base_wallets_dir = "wallets_to_send"
        wallets = []
        for member_id in mint.wallets:
            member_name = get_member_name_by_id(member_id)
            for i, wallet in enumerate(mint.wallets[member_id], 1):
                wallets.append((f"{member_name}{i}", wallet))
        if not os.path.exists(base_wallets_dir):
            os.mkdir(base_wallets_dir)
        timestamp = int(time.time())
        files = {
            "urban": os.path.join(base_wallets_dir, f"{release_id}{timestamp}UR.txt"),
            "pepper": os.path.join(base_wallets_dir, f"{release_id}{timestamp}PP.csv"),
            "minter_suite": os.path.join(base_wallets_dir, f"{release_id}{timestamp}MS.csv")
        }
        create_wallets_files(wallets, files)
        await interaction.response.send_message(files=[discord.File(files[key]) for key in files])
