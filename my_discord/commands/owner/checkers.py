import discord
from discord import app_commands

from base_classes.transaction import get_transaction
from my_discord import embeds
from my_discord.checkers import owner_checker
from utilities.logging import get_logger

logger = get_logger(__name__)
__all__ = ["OwnerCheckers"]


class OwnerCheckers(app_commands.Group):
    @app_commands.command(name="check-transaction",
                          description="OWNER COMMAND get transaction data from in-bot database")
    @app_commands.check(owner_checker)
    @app_commands.describe(transaction_hash="Hash to check")
    async def check_transaction(self, interaction: discord.Interaction, transaction_hash: str) -> None:
        tx = await get_transaction(transaction_hash)
        await interaction.response.send_message(embed=embeds.transaction_info(tx))
