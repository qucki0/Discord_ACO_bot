import time

import discord
from discord import app_commands

from additions import embeds
from additions.all_data import aco_members, config, submitted_transactions
from additions.autocomplete import unpaid_release_ids_autocomplete
from classes.blockchain import SubmitTransaction
from classes.classes import Transaction
from functions.blockchain import check_valid_transaction
from functions.mints import get_data_by_id_from_list


@app_commands.guild_only()
class Payments(app_commands.Group):
    @app_commands.command(name="pay", description="Make payment for chosen release and amount of checkouts")
    @app_commands.autocomplete(release_id=unpaid_release_ids_autocomplete)
    @app_commands.describe(release_id="Release name from /payments check-payments",
                           checkouts_quantity="The amount of checkouts you want to pay.")
    @discord.app_commands.rename(release_id="release_name")
    async def pay(self, interaction: discord.Interaction, release_id: str, checkouts_quantity: int):
        confirm_button = discord.ui.Button(label="Submit transaction", style=discord.ButtonStyle.green)
        member_id = interaction.user.id
        member = get_data_by_id_from_list(member_id, aco_members)
        if release_id not in member.payments:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return
        if checkouts_quantity > member.payments[release_id]["unpaid_amount"] or checkouts_quantity <= 0:
            await interaction.response.send_message("Wrong checkouts quantity", ephemeral=True)
            return

        async def confirm_payment_response(first_interaction: discord.Interaction):
            transaction_modal = SubmitTransaction()
            await first_interaction.response.send_modal(transaction_modal)
            await transaction_modal.wait()
            status, sol_amount = check_valid_transaction(transaction_modal.tx_hash)
            if sol_amount != -1:
                member.payments[release_id]["unpaid_amount"] = max(0, member.payments[release_id][
                    "unpaid_amount"] - checkouts_quantity)
                transaction = Transaction(member, transaction_modal.tx_hash, sol_amount, int(time.time()))
                submitted_transactions.append(transaction)
            await interaction.delete_original_response()
            await wallet_message.delete()
            await transaction_modal.interaction.response.send_message(
                embeds=embeds.transaction_status(status, sol_amount, member, transaction_modal.tx_hash))

        confirm_button.callback = confirm_payment_response
        view = discord.ui.View(timeout=600)
        view.add_item(confirm_button)
        await interaction.response.send_message("Please send $SOL to address in message below and click on button",
                                                view=view)
        wallet_message = await interaction.client.get_channel(interaction.channel_id).send(config.payment_wallet)

    @app_commands.command(name="check-unpaid", description="Command to check your unpaid successes")
    async def check_unpaid(self, interaction: discord.Interaction):
        member = get_data_by_id_from_list(interaction.user.id, aco_members)
        await interaction.response.send_message(embed=embeds.unpaid_successes(member))
