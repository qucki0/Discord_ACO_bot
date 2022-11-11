import hashlib
import time

import discord
from discord import app_commands

from base_classes.member import get_member_by_user
from my_discord import embeds
from utilities.logging import get_logger

logger = get_logger(__name__)
__all__ = ["WalletManager"]


@app_commands.guild_only()
class WalletManager(app_commands.Group):
    @app_commands.command(name="download", description="Get link to download Wallet Manager")
    async def download(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Don't forget to create a key using `/wallet-manager get-key`",
                                                embed=embeds.wallet_manager_download())

    @app_commands.command(name="get-key", description="Get Key for you wallet manager")
    async def get_key(self, interaction: discord.Interaction) -> None:
        exp_timestamp = 1664312400
        current_timestamp = time.time()
        week = 7 * 24 * 60 * 60
        while exp_timestamp < current_timestamp:
            exp_timestamp += week
        name = (await get_member_by_user(interaction.user)).name.lower()
        key = hashlib.sha256(f"{name}{exp_timestamp}".encode("utf8")).hexdigest()
        await interaction.response.send_message(embed=embeds.wallet_manager_login_data(name, key, exp_timestamp))

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await interaction.response.send_message(
            "An unexpected error occurred, try again. If that doesn't work, ping the admin")
        logger.exception(f"{interaction.user} {interaction.user.id} got error \n {error}")
