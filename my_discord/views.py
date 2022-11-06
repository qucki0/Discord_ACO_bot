import discord

from base_classes.member import check_admin, get_member_by_user, Member
from base_classes.mint import add_mint_to_mints_list, Mint
from base_classes.wallet import add_wallets_to_mint
from blockchains.solana.functions import submit_transaction, get_transaction_hash_from_string
from my_discord import embeds
from utilities.logging import get_logger
from utilities.strings import get_wallets_from_string

logger = get_logger(__name__)


class SubmitTransactionView(discord.ui.View):
    def __init__(self, original_interaction: discord.Interaction, member: Member, release_id: str,
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
        status, sol_amount = submit_transaction(tx_hash, self.member.id, self.release_id, self.checkouts_quantity)
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
        else:
            self.link = str(self.link)
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

    @discord.ui.button(label="Create ticket", style=discord.ButtonStyle.gray, custom_id="ticket_button")
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
        logger.debug(f"Ticket created for {ticket_interaction.user}, {ticket_interaction.user.name}")
        await channel.send(view=TicketView(self.closed_category_id), embed=embeds.ticket())
        await ticket_interaction.response.send_message(f"Ticket created {channel.mention}", ephemeral=True)
        member = get_member_by_user(ticket_interaction.user)
        member.ticket_id = channel.id


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
        logger.debug(f"Ticket closed for {close_interaction.user.id}, {close_interaction.user.name}")
        member = get_member_by_user(close_interaction.user)
        member.ticket_id = None
        self.stop()

    @discord.ui.button(label="Help", style=discord.ButtonStyle.blurple, custom_id="get_help")
    async def get_help(self, help_interaction: discord.Interaction, button: discord.ui.Button):
        await help_interaction.response.send_message(embeds=embeds.help_embeds())


class SendWalletsView(discord.ui.View):
    def __init__(self, original_interaction: discord.Interaction, member_id: int, mint: Mint) -> None:
        self.original_interaction = original_interaction
        self.member_id = member_id
        self.mint = mint
        super().__init__(timeout=600)

    @discord.ui.button(label="Send wallets", style=discord.ButtonStyle.green)
    async def send_wallets(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        send_wallets_modal = SendWalletsModal()
        await interaction.response.send_modal(send_wallets_modal)
        await send_wallets_modal.wait()

        wallets_str = send_wallets_modal.wallets_str
        wallets = get_wallets_from_string(wallets_str)

        if not len(wallets):
            await interaction.response.send_message("Please input wallets keys")
            return

        if self.mint.wallets_limit < len(wallets):
            await interaction.response.send_message(
                f"There are only {self.mint.wallets_limit} spots left for `{self.mint.id}`")
            return
        response = add_wallets_to_mint(wallets, self.mint, self.member_id)
        await send_wallets_modal.interaction.response.send_message(response)
        await self.original_interaction.edit_original_response(view=self)
        self.disable_buttons()

    async def on_timeout(self) -> None:
        self.disable_buttons()
        await self.original_interaction.edit_original_response(
            content="**EXPIRED, TRY AGAIN**",
            view=self
        )

    def disable_buttons(self) -> None:
        for button in self.children:
            button.disabled = True


class SendWalletsModal(discord.ui.Modal, title='Submit transaction'):
    wallets_str = discord.ui.TextInput(label='Your wallets private keys separated by spaces',
                                       placeholder="key1 key2 key3 ...")
    interaction = None

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction
        self.wallets_str = str(self.wallets_str)
        self.stop()
