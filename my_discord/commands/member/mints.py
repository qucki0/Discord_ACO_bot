import discord
from discord import app_commands

from base_classes.mint import is_mint_exist, get_actual_mints
from my_discord.views import RequestMintView
from setup import config
from utilities.logging import get_logger

logger = get_logger(__name__)
__all__ = ["Mints"]


@app_commands.guild_only()
class Mints(app_commands.Group):
    @app_commands.command(name="get-all", description="Get actual mints")
    async def get_mints(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        actual_mints = get_actual_mints()
        embeds_to_send = [mint.get_as_embed() for mint in actual_mints]
        message_to_send = "**Let us know if we lost something. Just use `/mints request` for it!**"
        await interaction.followup.send(message_to_send, embeds=embeds_to_send[:min(10, len(embeds_to_send))])
        for i in range(1, len(embeds_to_send) // 10 + 1):
            await interaction.channel.send(embeds=embeds_to_send[10 * i:min(10 * (i + 1), len(embeds_to_send))])

    @app_commands.command(name="request", description="Create request to add mint")
    @app_commands.describe(release_name="Name of release you want to request")
    @discord.app_commands.rename(release_name="release_name")
    async def request_mint(self, interaction: discord.Interaction, release_name: str) -> None:
        await interaction.response.defer()
        admins_to_ping = ""
        if is_mint_exist(mint_name=release_name):
            await interaction.followup.send(f"`{release_name}` already exist!", ephemeral=True)
            return
        for admin_id in config.admins:
            admins_to_ping += "<@" + str(admin_id) + "> "
        view = RequestMintView(interaction, release_name)
        await interaction.followup.send(f"{admins_to_ping}, please add `{release_name}`", view=view)

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await interaction.followup.send(
            "An unexpected error occurred, try again. If that doesn't help, ping the admin")
        logger.exception(f"{interaction.user} {interaction.user.id} got error \n {error}")
