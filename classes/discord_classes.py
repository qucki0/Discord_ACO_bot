import discord

from additions import embeds
from classes.classes import ACOMember
from functions.blockchain import submit_transaction, get_transaction_hash_from_string
from functions.members import check_admin
from functions.mints import add_mint_to_mints_list


class SubmitTransactionView(discord.ui.View):
    def __init__(self, original_interaction: discord.Interaction, member: ACOMember, release_id: str,
                 checkouts_quantity: int) -> None:
        self.original_interaction = original_interaction
        self.member = member
        self.release_id = release_id
        self.checkouts_quantity = checkouts_quantity
        self.wallet_message = None
        super().__init__(timeout=600)

    @discord.ui.button(label="Submit transaction", style=discord.ButtonStyle.green)
    async def submit_transaction(self, confirm_interaction: discord.Interaction,
                                 button: discord.ui.Button) -> None:
        transaction_modal = SubmitTransactionModal()
        await confirm_interaction.response.send_modal(transaction_modal)
        await transaction_modal.wait()

        tx_hash = transaction_modal.tx_hash
        status, sol_amount = submit_transaction(tx_hash, self.member, self.release_id, self.checkouts_quantity)
        if sol_amount != -1:
            await self.original_interaction.delete_original_response()
            await self.wallet_message.delete()
            tx_hash = get_transaction_hash_from_string(transaction_modal.tx_hash)
        await transaction_modal.interaction.response.send_message(
            embeds=embeds.transaction_status(status, sol_amount, self.member, tx_hash))

    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
        await self.original_interaction.edit_original_response(
            content="~~Please send $SOL to address in message below and click on button~~\n**EXPIRED, TRY AGAIN**",
            view=self
        )
        await self.wallet_message.delete()


class SubmitTransactionModal(discord.ui.Modal, title='Submit transaction'):
    tx_hash = discord.ui.TextInput(label='Transaction hash or solscan link', placeholder="Transaction", max_length=150)
    interaction = None

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction
        self.tx_hash = str(self.tx_hash)
        self.stop()


class RequestMintView(discord.ui.View):
    def __init__(self, original_interaction: discord.Interaction, release_id: str) -> None:
        self.original_interaction = original_interaction
        self.release_id = release_id
        super().__init__()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_response(self, accept_interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not check_admin(accept_interaction.user.id):
            await accept_interaction.response.send_message(
                "You do not have enough permissions to do perform this operation.", ephemeral=True)
            return
        add_mint_modal = AddMintModal()
        await accept_interaction.response.send_modal(add_mint_modal)
        await add_mint_modal.wait()
        await add_mint_to_mints_list(add_mint_modal.interaction, add_mint_modal.release_name, add_mint_modal.link,
                                     add_mint_modal.timestamp, add_mint_modal.wallets_limit)
        await self.original_interaction.edit_original_response(
            content=f":green_circle:Request for `{self.release_id}` accepted",
            view=None)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject_response(self, reject_interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not check_admin(reject_interaction.user.id):
            await reject_interaction.response.send_message(
                "You do not have enough permissions to do perform this operation.", ephemeral=True)
            return
        await self.original_interaction.edit_original_response(
            content=f":red_circle:Request for `{self.release_id}` rejected", view=None)


class AddMintModal(discord.ui.Modal, title='Create mint'):
    release_name = discord.ui.TextInput(label='Release name')
    wallets_limit = discord.ui.TextInput(label='Wallets limit')
    link = discord.ui.TextInput(label='Link', required=False)
    timestamp = discord.ui.TextInput(label='Timestamp', required=False)
    interaction = None

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.release_name = str(self.release_name)
        if str(self.link) == "":
            self.link = None
        if str(self.timestamp) == "":
            self.timestamp = None
        else:
            self.timestamp = int(str(self.timestamp))
        self.wallets_limit = int(str(self.wallets_limit))
        self.interaction = interaction
        self.stop()


class CreateTicketView(discord.ui.View):
    closed_category_id = None

    def __init__(self, closed_category_id: int):
        self.closed_category_id = closed_category_id
        super().__init__(timeout=None)

    @discord.ui.button(label="Create ticket", style=discord.ButtonStyle.blurple, custom_id="ticket_button")
    async def create_ticket(self, ticket_interaction: discord.Interaction, button: discord.ui.Button) -> None:
        ticket_name = f"{ticket_interaction.user.name}-{ticket_interaction.user.discriminator}".lower().replace(" ",
                                                                                                                "-")
        ticket = discord.utils.get(ticket_interaction.guild.text_channels, name=ticket_name)
        if ticket is not None:
            await ticket_interaction.response.send_message(f"You already have a ticket at {ticket.mention}",
                                                           ephemeral=True)
            return

        overwrites = {ticket_interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                      ticket_interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                                           attach_files=True)}
        category = ticket_interaction.channel.category
        channel = await ticket_interaction.guild.create_text_channel(name=ticket_name, overwrites=overwrites,
                                                                     category=category,
                                                                     reason=f"Ticket for"
                                                                            f" {ticket_interaction.user.mention}")
        await channel.send(f"{ticket_interaction.user.mention} Welcome", view=TicketView(self.closed_category_id))
        await ticket_interaction.response.send_message(f"Ticket created {channel.mention}", ephemeral=True)


class TicketView(discord.ui.View):
    closed_category_id = None

    def __init__(self, closed_category: int):
        self.closed_category_id = closed_category
        super().__init__(timeout=None)

    @discord.ui.button(label="Close ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def close_ticket(self, close_interaction: discord.Interaction, button: discord.ui.Button):
        closed_category = discord.utils.get(close_interaction.guild.categories, id=self.closed_category_id)
        channel_name = close_interaction.channel.name
        await close_interaction.channel.edit(category=closed_category, name=f"closed-{channel_name}",
                                             sync_permissions=True)
        await close_interaction.response.send_message(f"Ticket closed by {close_interaction.user.mention}")
        self.stop()
