import discord
from discord import app_commands

import config
from additions.all_data import actual_mints, aco_members
from additions.embeds import Embeds
from additions.functions import check_admin, get_mint_by_id, get_data_by_id_from_list, add_member, \
    add_mint_to_mints_list, check_mint_exist


class Mints(app_commands.Group):
    @app_commands.command(name="get-all", description="Get actual mints")
    async def get_mints(self, interaction: discord.Interaction):
        data_to_send = [mint.get_as_embed() for mint in actual_mints]
        message_to_send = "**Let us know if we lost something. Just use `/mints request` for it!**"
        await interaction.response.send_message(message_to_send, embeds=data_to_send[:min(10, len(data_to_send))])
        for i in range(1, len(data_to_send) // 10 + 1):
            await interaction.client.get_channel(interaction.channel_id).send(
                embeds=data_to_send[10 * i:min(10 * (i + 1), len(data_to_send))])

    @app_commands.command(name="request", description="Create request to add mint")
    async def request_mint(self, interaction: discord.Interaction, release_id: str, link: str = None,
                           mint_time: str = None):
        admins_to_ping = ""
        if check_mint_exist(release_id):
            await interaction.response.send_message(f"`{release_id}` already exist!", ephemeral=True)
            return
        for admin_id in config.ADMINS_IDS:
            admins_to_ping += "<@" + str(admin_id) + "> "
        accept_button = discord.ui.Button(label="Accept", style=discord.ButtonStyle.green)
        reject_button = discord.ui.Button(label="Reject", style=discord.ButtonStyle.red)

        async def accept_response(accept_interaction: discord.Interaction):
            if not check_admin(accept_interaction.user.id):
                await accept_interaction.response.send_message("Not enough rights to do it", ephemeral=True)
                return
            await add_mint_to_mints_list(accept_interaction, release_id, link, mint_time)
            await interaction.delete_original_response()
            await accept_interaction.client.get_channel(accept_interaction.channel_id).send(
                f":green_circle:Request for {release_id} Accepted")

        async def reject_response(reject_interaction: discord.Interaction):
            if not check_admin(reject_interaction.user.id):
                await reject_interaction.response.send_message("Not enough rights to do it", ephemeral=True)
                return
            await interaction.delete_original_response()
            await reject_interaction.client.get_channel(reject_interaction.channel_id).send(
                ":red_circle:Request Rejected")

        accept_button.callback = accept_response
        reject_button.callback = reject_response
        view = discord.ui.View(timeout=None)
        view.add_item(accept_button)
        view.add_item(reject_button)

        await interaction.response.send_message(
            f"{admins_to_ping}, please add `{release_id}`, link:`{link}`, time: `{mint_time}`", view=view)


class Wallets(app_commands.Group):
    @app_commands.command(name="send", description="Send wallets separated by commas for chosen release")
    async def send_wallets(self, interaction: discord.Interaction, release_id: str, wallets: str):
        member_id = interaction.user.id
        member = get_data_by_id_from_list(interaction.user.id, aco_members)
        if member is None:
            add_member(interaction.user)
        if not len(wallets):
            await interaction.response.send_message("Please input wallets keys")
            return

        wallets = [wallet.strip() for wallet in wallets.split(",")]

        mint = get_mint_by_id(release_id)
        if mint is not None:
            if member_id not in mint.wallets:
                mint.wallets[member_id] = set()
            number_of_wallets = len(mint.wallets[member_id])
            for wallet in wallets:
                mint.wallets[member_id].add(wallet)
            await interaction.response.send_message(
                f"Successfully sent {len(mint.wallets[member_id]) - number_of_wallets} wallets,"
                f" other {len(wallets) - (len(mint.wallets[member_id]) - number_of_wallets)} already exist")
        else:
            await interaction.response.send_message(f"There are no releases named as {release_id}")

    @app_commands.command(name="check", description="Check the wallets that you sent")
    async def check_wallets(self, interaction: discord.Interaction, release_id: str):
        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}", ephemeral=True)
            return
        member_id = interaction.user.id
        member_name = interaction.user.name
        message_to_send = f"{member_name} wallets for `{mint.id}`:\n```\n"
        if member_id not in mint.wallets:
            await interaction.response.send_message(message_to_send + "Nothing\n```\n")
            return
        for wallet in mint.get_wallets_by_id(member_id):
            message_to_send += f"{wallet}\n"
        message_to_send += "```"
        await interaction.response.send_message(message_to_send)

    @app_commands.command(name="delete",
                          description='Delete wallets separated by commas for chosen release, "all" for all')
    async def delete_wallets(self, interaction: discord.Interaction, release_id: str, wallets: str):
        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return
        member_id = interaction.user.id
        if member_id not in mint.wallets:
            await interaction.response.send_message(f"You need to submit wallets firstly!")
            return

        counter = len(mint.wallets[member_id])
        if wallets.lower().strip() == "all":
            mint.wallets[member_id].clear()
        else:
            wallets_to_delete = [wallet.strip() for wallet in wallets.split(",")]
            for wallet in wallets_to_delete:
                mint.wallets[member_id].discard(wallet)
        await interaction.response.send_message(
            f"Successfully deleted {counter - len(mint.wallets[member_id])} wallets")


class Payments(app_commands.Group):
    @app_commands.command(name="pay", description="Make payment for chosen release and amount of checkouts")
    async def pay(self, interaction: discord.Interaction, release_name: str, amount_to_pay: float,
                  checkouts_quantity: int):
        button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.green)
        member_id = interaction.user.id
        member = get_data_by_id_from_list(member_id, aco_members)
        if checkouts_quantity > member.payments[release_name]["unpaid_amount"] or checkouts_quantity <= 0:
            await interaction.response.send_message("Wrong checkouts quantity", ephemeral=True)
            return

        async def first_response(first_interaction: discord.Interaction):
            admins_to_ping = ""
            for admin_id in config.ADMINS_IDS:
                admins_to_ping += "<@" + str(admin_id) + "> "
            button.callback = second_response
            await first_interaction.response.edit_message(
                content=f"{admins_to_ping}, check *{amount_to_pay} $SOL* payment.", view=view)

        async def second_response(second_interaction: discord.Interaction):
            if not check_admin(second_interaction.user.id):
                await second_interaction.response.send_message("Not enough rights to do it", ephemeral=True)
                return

            member.payments[release_name]["unpaid_amount"] -= checkouts_quantity
            await second_interaction.response.edit_message(
                content=f"Payment *{amount_to_pay} $SOL* for `{release_name}` successful", view=None)

        button.callback = first_response
        view = discord.ui.View(timeout=None)
        view.add_item(button)

        await interaction.response.send_message(
            f"Send {amount_to_pay} $SOL to `pay1L1NNvAgjgWiPQMR3G5RwSLcDLpPtbG2VGchZWEh` and click button below after "
            f"success",
            view=view)

    @app_commands.command(name="check-payments", description="Command to check your unpaid successes")
    async def check_payments(self, interaction: discord.Interaction, user: discord.Member = None):
        if user is None:
            member = get_data_by_id_from_list(interaction.user.id, aco_members)
        else:
            if not check_admin(interaction.user.id):
                await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
                return
            member = get_data_by_id_from_list(user.id, aco_members)

        if member is None:
            await interaction.response.send_message("Nothing to see, take your first ACO!", ephemeral=True)
            return

        await interaction.response.send_message(embed=Embeds.unpaid_successes(member))
