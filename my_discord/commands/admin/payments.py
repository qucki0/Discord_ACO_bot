import discord
from discord import app_commands

from base_classes.member import get_member_by_user, get_member_by_id
from base_classes.mint import get_mint_by_name
from base_classes.payment import add_checkout
from my_discord import embeds
from my_discord.autocomplete import all_releases_autocomplete
from my_discord.checkers import admin_checker

__all__ = ["AdminPayments"]


@app_commands.guild_only()
class AdminPayments(app_commands.Group):
    @app_commands.command(name="add-success", description="ADMIN COMMAND Add success to chosen release for chosen user")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_id=all_releases_autocomplete)
    @app_commands.describe(release_id="Mint name from /admin-mints get-all-mints-list or /mints get-all",
                           amount="amount of checkouts")
    async def add_success(self, interaction: discord.Interaction, release_id: str, amount: int,
                          user: discord.Member) -> None:
        mint = get_mint_by_name(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return

        member = get_member_by_user(user)
        payment = add_checkout(member, mint, amount)

        await interaction.response.send_message(f"Added {amount} checkouts", ephemeral=True)
        if member.ticket_id is not None:
            await interaction.client.get_channel(member.ticket_id).send(
                embed=embeds.success(user.name, release_id, payment.amount_of_checkouts))

    @app_commands.command(name="check-payments", description="Command to check your unpaid successes")
    @app_commands.check(admin_checker)
    async def check_payments(self, interaction: discord.Interaction, user: discord.Member) -> None:
        member = get_member_by_id(user.id)
        await interaction.response.send_message(embed=embeds.unpaid_successes(member))