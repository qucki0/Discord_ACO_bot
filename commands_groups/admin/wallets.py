import os
import time

import discord
from discord import app_commands

from additions.autocomplete import release_id_autocomplete
from additions.checkers import admin_checker
from functions.files import create_csv_from_dict
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
        wallets = ""
        wallets_as_dict = []
        another_wallets_as_dict = []
        for member_id in mint.wallets:
            for i, wallet in enumerate(mint.wallets[member_id], 1):
                member_name = get_member_name_by_id(member_id)
                wallets += f"{member_name}{i}:{wallet}\n"
                wallets_as_dict.append({"ALIAS": f"{member_name}{i}",
                                        "PRIVATE_KEY": wallet})
                another_wallets_as_dict.append({"Name": f"{member_name}{i}",
                                                "Private Key": wallet,
                                                "Public Key": ""})
        if not os.path.exists(base_wallets_dir):
            os.mkdir(base_wallets_dir)
        timestamp = int(time.time())
        txt_file_name = os.path.join(base_wallets_dir, f"{release_id}{timestamp}UR.txt")
        csv_file_name = os.path.join(base_wallets_dir, f"{release_id}{timestamp}PP.csv")
        another_csv_file_name = os.path.join(base_wallets_dir, f"{release_id}{timestamp}MS.csv")
        with open(txt_file_name, "w") as file:
            file.write(wallets)
        create_csv_from_dict(csv_file_name, wallets_as_dict)
        create_csv_from_dict(another_csv_file_name, another_wallets_as_dict)
        time.sleep(1)
        await interaction.response.send_message(files=[discord.File(txt_file_name), discord.File(csv_file_name),
                                                       discord.File(another_csv_file_name)])
