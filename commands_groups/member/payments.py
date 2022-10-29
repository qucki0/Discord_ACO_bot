import discord
from discord import app_commands

from additions import embeds
from additions.all_data import config
from additions.autocomplete import unpaid_release_ids_autocomplete
from classes.discord_classes import SubmitTransactionView
from functions import sql_commands
from functions.members import get_member_by_user


@app_commands.guild_only()
class Payments(app_commands.Group):
    @app_commands.command(name="pay", description="Make payment for chosen release and amount of checkouts")
    @app_commands.autocomplete(release_id=unpaid_release_ids_autocomplete)
    @app_commands.describe(release_id="Release name from /payments check-payments",
                           checkouts_quantity="The amount of checkouts you want to pay.")
    @discord.app_commands.rename(release_id="release_name")
    async def pay(self, interaction: discord.Interaction, release_id: str, checkouts_quantity: int) -> None:
        member_id = interaction.user.id
        member = get_member_by_user(interaction.user)
        if not sql_commands.check_exist.payment(release_id, member_id):
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return
        payment = sql_commands.get.payment(release_id, member_id)
        if checkouts_quantity > payment.amount_of_checkouts or checkouts_quantity <= 0:
            await interaction.response.send_message("Wrong checkouts quantity", ephemeral=True)
            return
        view = SubmitTransactionView(interaction, member, release_id, checkouts_quantity)
        await interaction.response.send_message("Please send $SOL to address in message below and click on button",
                                                view=view)
        view.wallet_message = await interaction.client.get_channel(interaction.channel_id).send(config.payment_wallet)

    @app_commands.command(name="check-unpaid", description="Command to check your unpaid successes")
    async def check_unpaid(self, interaction: discord.Interaction) -> None:
        member = get_member_by_user(interaction.user)
        await interaction.response.send_message(embed=embeds.unpaid_successes(member))
