import discord
from discord import app_commands

from my_discord.checkers import admin_checker
from setup import config
from utilities.files import create_backup
from utilities.logging import get_logger

logger = get_logger(__name__)
__all__ = ["Admin"]


@app_commands.guild_only()
class Admin(app_commands.Group):
    @app_commands.command(name="backup", description="ADMIN COMMAND just doing backup")
    @app_commands.check(admin_checker)
    async def backup(self, interaction: discord.Interaction) -> None:
        await create_backup(interaction.client.get_channel(config.ids.channels.backup_channel_id))
        await interaction.response.send_message(f"Backup successful, check <#{config.ids.channels.backup_channel_id}>")
