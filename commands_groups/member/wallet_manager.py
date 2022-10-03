import hashlib
import time

import discord
from discord import app_commands

from additions import embeds
from functions.members import get_member_name_by_id


@app_commands.guild_only()
class WalletManager(app_commands.Group):
    @app_commands.command(name="download", description="Get link to download Wallet Manager")
    async def download(self, interaction: discord.Interaction):
        await interaction.response.send_message("Don't forget to create a key using `/wallet-manager get-key`",
                                                embed=embeds.wallet_manager_download())

    @app_commands.command(name="get-key", description="Get Key for you wallet manager")
    async def get_key(self, interaction: discord.Interaction):
        exp_timestamp = 1664312400
        current_timestamp = time.time()
        while exp_timestamp < current_timestamp:
            exp_timestamp += 7 * 24 * 60 * 60
        name = get_member_name_by_id(interaction.user.id).lower()
        key = hashlib.sha256(f"{name}{exp_timestamp}".encode("utf8")).hexdigest()
        await interaction.response.send_message(embed=embeds.wallet_manager_login_data(name, key, exp_timestamp))
