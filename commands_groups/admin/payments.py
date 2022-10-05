import discord
from discord import app_commands

from additions import embeds
from additions.all_data import aco_members, all_mints
from additions.checkers import admin_checker
from functions.members import add_member
from functions.mints import get_data_by_id_from_list
from additions.autocomplete import possible_releases_to_add_payment

@app_commands.guild_only()
class AdminPayments(app_commands.Group):
    @app_commands.command(name="add-success", description="ADMIN COMMAND Add success to chosen release for chosen user")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_id=possible_releases_to_add_payment)
    @app_commands.describe(release_id="Mint name from /admin-mints get-all-mints-list or /mints get-all",
                           amount="amount of checkouts")
    async def add_success(self, interaction: discord.Interaction, release_id: str, amount: int, user: discord.Member):
        mint = get_data_by_id_from_list(release_id, all_mints)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return
        member = get_data_by_id_from_list(user.id, aco_members)
        if member is None:
            add_member(user)
        member = get_data_by_id_from_list(user.id, aco_members)
        if mint.id not in member.payments:
            member.payments[mint.id] = {"amount_of_checkouts": amount,
                                        "unpaid_amount": amount}
        else:
            member.payments[mint.id]["amount_of_checkouts"] += amount
            member.payments[mint.id]["unpaid_amount"] += amount
        mint.checkouts += amount
        await interaction.response.send_message(f"Added {amount} checkouts", ephemeral=True)
        await interaction.client.get_channel(interaction.channel_id).send(
            embed=embeds.success(user.name, release_id, member.payments[mint.id]["amount_of_checkouts"]))

    @app_commands.command(name="check-payments", description="Command to check your unpaid successes")
    @app_commands.check(admin_checker)
    async def check_payments(self, interaction: discord.Interaction, user: discord.Member):
        member = get_data_by_id_from_list(user.id, aco_members)
        await interaction.response.send_message(embed=embeds.unpaid_successes(member))
