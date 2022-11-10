import discord
from discord.ext import commands

from base_classes.payment import auto_send_notifications
from my_discord.views.tickets import CreateTicketView, TicketView
from setup import config
from utilities.files import auto_backup
from utilities.logging import get_logger
from .commands.admin import *
from .commands.member import *
from .commands.owner import *

logger = get_logger(__name__)


class DiscordClient(commands.Bot):
    def __init__(self, prefix: str = "!") -> None:
        super().__init__(intents=discord.Intents.all(), command_prefix=prefix)
        groups = [Admin, AdminMints, AdminPayments, AdminWallets,
                  Mints, Wallets, Payments, WalletManager,
                  Owner, OwnerCheckers, OwnerStatistic]
        self.tree.add_command(ask_help)

        for group in groups:
            self.tree.add_command(group())

    async def setup_hook(self) -> None:
        self.add_view(CreateTicketView(config.closed_category_id))
        self.add_view(TicketView(config.closed_category_id))
        await self.tree.sync()
        self.loop.create_task(auto_send_notifications(self))
        self.loop.create_task(auto_backup(self))
        logger.info(f'{self.user} has connected to Discord!')

    async def on_error(self, event_method: str, /, *args, **kwargs) -> None:
        logger.error(event_method)
