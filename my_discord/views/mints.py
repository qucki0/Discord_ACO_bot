import discord

from base_classes.member import is_member_admin
from base_classes.mint import add_mint_to_mints_list
from utilities.logging import get_logger

logger = get_logger(__name__)


class RequestMintView(discord.ui.View):
    def __init__(self, original_interaction: discord.Interaction, release_id: str) -> None:
        self.original_interaction = original_interaction
        self.release_id = release_id
        super().__init__()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_response(self, accept_interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not is_member_admin(accept_interaction.user.id):
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
        if not is_member_admin(reject_interaction.user.id):
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
