import discord
from discord import app_commands

from additions import embeds
from additions.all_data import aco_members, config
from additions.autocomplete import unpaid_release_ids_autocomplete
from functions.members import check_admin
from functions.mints import get_data_by_id_from_list


@app_commands.guild_only()
class Payments(app_commands.Group):
    @app_commands.command(name="pay", description="Make payment for chosen release and amount of checkouts")
    @app_commands.autocomplete(release_id=unpaid_release_ids_autocomplete)
    @app_commands.describe(release_id="Release name from /payments check-payments",
                           amount_to_pay="Amount that you want to pay in $SOL",
                           checkouts_quantity="The amount of checkouts you want to pay.")
    @discord.app_commands.rename(release_id="release_name")
    async def pay(self, interaction: discord.Interaction, release_id: str, amount_to_pay: float,
                  checkouts_quantity: int):
        button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.green)
        member_id = interaction.user.id
        member = get_data_by_id_from_list(member_id, aco_members)
        if release_id not in member.payments:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return
        if checkouts_quantity > member.payments[release_id]["unpaid_amount"] or checkouts_quantity <= 0:
            await interaction.response.send_message("Wrong checkouts quantity", ephemeral=True)
            return

        async def first_response(first_interaction: discord.Interaction):
            admins_to_ping = ""
            for admin_id in config.admins:
                admins_to_ping += "<@" + str(admin_id) + "> "
            button.callback = second_response
            await first_interaction.response.edit_message(
                content=f"{admins_to_ping}, check *{amount_to_pay} $SOL* payment.", view=view)

        async def second_response(second_interaction: discord.Interaction):
            if not check_admin(second_interaction.user.id):
                await second_interaction.response.send_message(
                    "You do not have enough permissions to do perform this operation.", ephemeral=True)
                return

            member.payments[release_id]["unpaid_amount"] = max(0, member.payments[release_id][
                "unpaid_amount"] - checkouts_quantity)
            await second_interaction.response.edit_message(
                content=f"Payment *{amount_to_pay} $SOL* for `{release_id}` successful", view=None)

        button.callback = first_response
        view = discord.ui.View(timeout=None)
        view.add_item(button)

        await interaction.response.send_message(
            f"Send {amount_to_pay} $SOL to `pay1L1NNvAgjgWiPQMR3G5RwSLcDLpPtbG2VGchZWEh` and click button below after "
            f"success",
            view=view)

    @app_commands.command(name="check-payments", description="Command to check your unpaid successes")
    async def check_payments(self, interaction: discord.Interaction):
        member = get_data_by_id_from_list(interaction.user.id, aco_members)
        await interaction.response.send_message(embed=embeds.unpaid_successes(member))
