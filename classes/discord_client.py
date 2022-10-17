import discord
from discord.ext import commands

from commands_groups.admin_group import AdminMints, AdminWallets, Admin, AdminPayments
from commands_groups.member_group import Mints, Wallets, Payments, ask_help, WalletManager
from commands_groups.owner_group import Owner, OwnerCheckers, OwnerStatistic
from functions.files import auto_backup
from classes.discord_classes import CreateTicketView


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
        self.add_view(CreateTicketView())
        await self.tree.sync()
        self.loop.create_task(auto_backup(self))
        print(f'{self.user} has connected to Discord!')
