import discord
from discord import app_commands

from additions.all_data import config
from additions.checkers import admin_checker
from functions.files import do_backup


@app_commands.guild_only()
class Admin(app_commands.Group):
    @app_commands.command(name="backup", description="ADMIN COMMAND just doing backup")
    @app_commands.check(admin_checker)
    async def backup(self, interaction: discord.Interaction):
        await do_backup(interaction, skip_timestamp=True)
        await interaction.response.send_message(f"Backup successful, check <#{config.backup_channel_id}>")