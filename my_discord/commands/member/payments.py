import discord
from discord import app_commands

from base_classes.member import get_member_by_user
from base_classes.mint import get_mint_by_name
from base_classes.payment import get_payment, check_checkouts_to_pay_correct
from blockchains.handlers import get_payment_wallet
from my_discord import embeds
from my_discord.autocomplete import unpaid_release_ids_autocomplete
from my_discord.views.transactions import SubmitTransactionView
from utilities.logging import get_logger

logger = get_logger(__name__)
__all__ = ["Payments"]


@app_commands.guild_only()
class Payments(app_commands.Group):
    @app_commands.command(name="pay", description="Make payment for chosen release and amount of checkouts")
    @app_commands.autocomplete(release_name=unpaid_release_ids_autocomplete)
    @app_commands.describe(release_name="Release name from /payments check-payments",
                           checkouts_quantity="The amount of checkouts you want to pay.")
    @discord.app_commands.rename(release_name="release_name")
    async def pay(self, interaction: discord.Interaction, release_name: str, checkouts_quantity: int) -> None:
        await interaction.response.defer()
        member_id = interaction.user.id
        member = await get_member_by_user(interaction.user)
        payment = await get_payment(release_name, member_id)
        mint = await get_mint_by_name(release_name)
        check_checkouts_to_pay_correct(checkouts_quantity, payment)
        view = SubmitTransactionView(interaction, member, mint, checkouts_quantity)
        await interaction.followup.send(
            f"Please send ${mint.chain.upper()} to address in message below and click on button", view=view)
        view.wallet_message = await interaction.channel.send(get_payment_wallet(mint))

    @app_commands.command(name="check-unpaid", description="Command to check your unpaid successes")
    async def check_unpaid(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        member = await get_member_by_user(interaction.user)
        await interaction.followup.send(embed=await embeds.unpaid_successes(member))
