import discord
from discord import app_commands

import sql.commands
from blockchains.solana.functions import get_transaction_hash_from_string, is_hash_length_correct
from my_discord import embeds
from my_discord.checkers import owner_checker

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
        if sql.commands.check_exist.transaction(transaction_hash):
            tx = sql.commands.get.transaction(transaction_hash)
            await interaction.response.send_message(embed=embeds.transaction_info(tx))
        else:
            await interaction.response.send_message("Transaction not found")
