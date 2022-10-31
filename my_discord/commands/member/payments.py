import discord
from discord import app_commands

from base_classes.member import get_member_by_user
from base_classes.payment import get_payment, is_payment_exist
from my_discord import embeds
from my_discord.autocomplete import unpaid_release_ids_autocomplete
from my_discord.views import SubmitTransactionView
from setup import config

__all__ = ["Payments"]


@app_commands.guild_only()
class Payments(app_commands.Group):
    @app_commands.command(name="pay", description="Make payment for chosen release and amount of checkouts")
    @app_commands.autocomplete(release_name=unpaid_release_ids_autocomplete)
    @app_commands.describe(release_name="Release name from /payments check-payments",
                           checkouts_quantity="The amount of checkouts you want to pay.")
    @discord.app_commands.rename(release_name="release_name")
    async def pay(self, interaction: discord.Interaction, release_name: str, checkouts_quantity: int) -> None:
        member_id = interaction.user.id
        member = get_member_by_user(interaction.user)
        if not is_payment_exist(release_name, member_id):
            await interaction.response.send_message(f"There are no releases named as {release_name}")
            return
        payment = get_payment(release_name, member_id)
        if checkouts_quantity > payment.amount_of_checkouts or checkouts_quantity <= 0:
            await interaction.response.send_message("Wrong checkouts quantity", ephemeral=True)
            return
        view = SubmitTransactionView(interaction, member, release_name, checkouts_quantity)
        await interaction.response.send_message("Please send $SOL to address in message below and click on button",
                                                view=view)
        view.wallet_message = await interaction.client.get_channel(interaction.channel_id).send(config.payment_wallet)

    @app_commands.command(name="check-unpaid", description="Command to check your unpaid successes")
    async def check_unpaid(self, interaction: discord.Interaction) -> None:
        member = get_member_by_user(interaction.user)
        await interaction.response.send_message(embed=embeds.unpaid_successes(member))
