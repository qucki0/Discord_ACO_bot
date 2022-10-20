import discord
from discord.ext import commands

from additions.all_data import config
from classes.discord_classes import CreateTicketView, TicketView
from commands_groups.admin_group import AdminMints, AdminWallets, Admin, AdminPayments
from commands_groups.member_group import Mints, Wallets, Payments, ask_help, WalletManager
from commands_groups.owner_group import Owner, OwnerCheckers, OwnerStatistic
from functions.files import auto_backup
from functions.paymnets import auto_send_notifications


class DiscordClient(commands.Bot):
    def __init__(self, prefix: str = "!") -> None:
        super().__init__(intents=discord.Intents.all(), command_prefix=prefix)
        groups = [AdminMints, Admin, AdminPayments, AdminWallets,
                  Mints, Wallets, Payments, WalletManager,
                  Owner, OwnerCheckers, OwnerStatistic]
        self.tree.add_command(ask_help)
        for group in groups:
            self.tree.add_command(group())

    async def setup_hook(self) -> None:
        self.add_view(CreateTicketView(config.closed_category_id))
        self.add_view(TicketView(config.closed_category_id))
        await self.tree.sync()
        self.loop.create_task(auto_backup(self))
        self.loop.create_task(auto_send_notifications(self))
        print(f'{self.user} has connected to Discord!')
