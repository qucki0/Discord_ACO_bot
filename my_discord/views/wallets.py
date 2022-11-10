import discord

from base_classes.mint import Mint
from base_classes.wallet import add_wallets_to_mint
from utilities.logging import get_logger
from utilities.strings import get_wallets_from_string

logger = get_logger(__name__)


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
