import discord
from discord import app_commands

from additions.autocomplete import all_releases_autocomplete
from additions.checkers import owner_checker
from additions.embeds import mint_info
from functions.mints import get_mint_by_id, get_unpaid_mints


class OwnerStatistic(app_commands.Group):
    @app_commands.command(name="mint", description="OWNER COMMAND checking member stats")
    @app_commands.check(owner_checker)
    @app_commands.describe(release_id="Release name")
    @app_commands.autocomplete(release_id=all_releases_autocomplete)
    async def mint_statistic(self, interaction: discord.Interaction, release_id: str) -> None:
        mint = get_mint_by_id(release_id)
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
