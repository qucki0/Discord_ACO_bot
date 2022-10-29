import discord
from discord import app_commands

from additions import embeds
from additions.checkers import owner_checker
from functions import sql_commands
from functions.blockchain import get_transaction_hash_from_string, is_hash_length_correct


class OwnerCheckers(app_commands.Group):
    @app_commands.command(name="check-transaction",
                          description="OWNER COMMAND get transaction data from in-bot database")
    @app_commands.check(owner_checker)
    @app_commands.describe(transaction_hash="Hash to check")
    async def check_transaction(self, interaction: discord.Interaction, transaction_hash: str) -> None:
        transaction_hash = get_transaction_hash_from_string(transaction_hash)
        if not is_hash_length_correct(transaction_hash):
            await interaction.response.send_message("Wrong input.", ephemeral=True)
        if sql_commands.check_exist.transaction(transaction_hash):
            tx = sql_commands.get.transaction(transaction_hash)
            await interaction.response.send_message(embed=embeds.transaction_info(tx))
        else:
            await interaction.response.send_message("Transaction not found")
