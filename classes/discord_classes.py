import discord

from additions import embeds
from classes.classes import ACOMember
from functions.blockchain import submit_transaction, get_transaction_hash_from_string


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
    async def submit_transaction_button(self, confirm_interaction: discord.Interaction,
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
    tx_hash = discord.ui.TextInput(label='Transaction hash or solscan link', style=discord.TextStyle.short,
                                   placeholder="Transaction", max_length=150, required=True)
    interaction = None

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction
        self.tx_hash = str(self.tx_hash)
        self.stop()
