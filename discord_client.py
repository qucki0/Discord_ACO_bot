import discord
from discord.ext import commands

from commands_groups.admin import AdminMints, AdminWallets, Admin, AdminPayments
from commands_groups.member import Mints, Wallets, Payments, ask_help


class DiscordClient(commands.Bot):
    def __init__(self, prefix="!"):
        super().__init__(intents=discord.Intents.all(), command_prefix=prefix)
        self.synced = False
        groups = [AdminMints, AdminWallets, Admin, AdminPayments, Mints, Wallets, Payments]
        self.tree.add_command(ask_help)
        for group in groups:
            self.tree.add_command(group())

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        print(f'{self.user} has connected to Discord!')
