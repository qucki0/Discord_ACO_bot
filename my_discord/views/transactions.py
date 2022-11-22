import discord

from base_classes.member import Member
from base_classes.mint import Mint
from blockchains.handlers import submit_transaction, get_transaction_hash_from_string
from my_discord import embeds
from utilities.logging import get_logger

logger = get_logger(__name__)


class SubmitTransactionView(discord.ui.View):
    def __init__(self, original_interaction: discord.Interaction, member: Member, mint: Mint,
                 checkouts_quantity: int) -> None:
        self.original_interaction = original_interaction
        self.member = member
        self.mint = mint
        self.checkouts_quantity = checkouts_quantity
        self.wallet_message = None
        super().__init__(timeout=600)

    @discord.ui.button(label="Submit transaction", style=discord.ButtonStyle.green)
    async def submit_transaction(self, confirm_interaction: discord.Interaction, button: discord.ui.Button) -> None:
        transaction_modal = SubmitTransactionModal()
        await confirm_interaction.response.send_modal(transaction_modal)
        await transaction_modal.wait()

        tx_hash = transaction_modal.tx_hash
        status, amount = await submit_transaction(tx_hash, self.member.id, self.mint, self.checkouts_quantity)
        if amount != -1:
            await self.original_interaction.delete_original_response()
            await self.wallet_message.delete()
            self.stop()
            tx_hash = get_transaction_hash_from_string(transaction_modal.tx_hash, self.mint)
        await transaction_modal.interaction.followup.send(
            embeds=await embeds.transaction_status(status, amount, self.member, tx_hash))

    async def on_timeout(self) -> None:
        self.disable_buttons()
        await self.original_interaction.edit_original_response(
            content="~~Please send $SOL to address in message below and click on button~~\n**EXPIRED, TRY AGAIN**",
            view=self
        )
        await self.wallet_message.delete()

    def disable_buttons(self) -> None:
        for button in self.children:
            button.disabled = True


class SubmitTransactionModal(discord.ui.Modal, title='Submit transaction'):
    tx_hash = discord.ui.TextInput(label='Transaction hash or block scanner link', placeholder="Transaction",
                                   max_length=150)
    interaction = None

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.interaction = interaction
        self.tx_hash = str(self.tx_hash)
        self.stop()
