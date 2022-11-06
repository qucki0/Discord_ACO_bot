import discord
from discord import app_commands

from base_classes.mint import get_mint_by_name
from base_classes.payment import get_unpaid_mints
from my_discord.autocomplete import all_releases_autocomplete
from my_discord.checkers import owner_checker
from my_discord.embeds import mint_info
from utilities.logging import get_logger

logger = get_logger(__name__)
__all__ = ["OwnerStatistic"]


class OwnerStatistic(app_commands.Group):
    @app_commands.command(name="mint", description="OWNER COMMAND checking member stats")
    @app_commands.check(owner_checker)
    @app_commands.describe(release_name="Release name")
    @app_commands.autocomplete(release_name=all_releases_autocomplete)
    async def mint_statistic(self, interaction: discord.Interaction, release_name: str) -> None:
        mint = get_mint_by_name(release_name)
        if mint is None:
            await interaction.response.send_message("No info about this mint")
            return
        await interaction.response.send_message(embed=mint_info(mint))

    @app_commands.command(name="unpaid", description="OWNER COMMAND checking member stats")
    @app_commands.check(owner_checker)
    async def unpaid(self, interaction: discord.Interaction) -> None:
        data = get_unpaid_mints()
        data_to_send = ""
        for release in data:
            data_to_send += f"**{release}:**\n"
            for member_id, amount in data[release]:
                data_to_send += f">  <@{member_id}>: {amount}\n"
            data_to_send += "\n"
        await interaction.response.send_message(data_to_send)

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await interaction.response.send_message(
            "An unexpected error occurred, try again. If that doesn't work, ping the admin")
        logger.exception(f"{interaction.user} {interaction.user.id} got error \n {error}")
