import discord
from discord import app_commands

from additions import embeds
from additions.autocomplete import all_releases_autocomplete
from additions.checkers import admin_checker
from functions.members import get_member_for_payments, get_member_by_id
from functions.mints import get_mint_by_id
from functions.paymnets import add_checkouts


@app_commands.guild_only()
class AdminPayments(app_commands.Group):
    @app_commands.command(name="add-success", description="ADMIN COMMAND Add success to chosen release for chosen user")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_id=all_releases_autocomplete)
    @app_commands.describe(release_id="Mint name from /admin-mints get-all-mints-list or /mints get-all",
                           amount="amount of checkouts")
    async def add_success(self, interaction: discord.Interaction, release_id: str, amount: int, user: discord.Member):
        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return

        member = get_member_for_payments(user)
        add_checkouts(member, mint, amount)

        await interaction.response.send_message(f"Added {amount} checkouts", ephemeral=True)
        await interaction.client.get_channel(interaction.channel_id).send(
            embed=embeds.success(user.name, release_id, member.payments[mint.id]["amount_of_checkouts"]))

    @app_commands.command(name="check-payments", description="Command to check your unpaid successes")
    @app_commands.check(admin_checker)
    async def check_payments(self, interaction: discord.Interaction, user: discord.Member):
        member = get_member_by_id(user.id)
        await interaction.response.send_message(embed=embeds.unpaid_successes(member))
