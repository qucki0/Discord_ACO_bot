import discord
from discord import app_commands

from base_classes.transaction import get_transaction
from blockchains.solana.functions import get_transaction_hash_from_string, is_hash_length_correct
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
        transaction_hash = get_transaction_hash_from_string(transaction_hash)
        if not is_hash_length_correct(transaction_hash):
            await interaction.response.send_message("Wrong input.", ephemeral=True)
        tx = get_transaction(transaction_hash)
        if tx is not None:
            await interaction.response.send_message(embed=embeds.transaction_info(tx))
        else:
            await interaction.response.send_message("Transaction not found")

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await interaction.response.send_message(
            "An unexpected error occurred, try again. If that doesn't work, ping the admin")
        logger.exception(f"{interaction.user} {interaction.user.id} got error \n {error}")
