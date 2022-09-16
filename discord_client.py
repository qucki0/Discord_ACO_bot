import discord
from discord.ext import commands

from command_groups import Mints, Aco, Admin, Payment


class DiscordClient(commands.Bot):
    def __init__(self, prefix="!"):
        super().__init__(intents=discord.Intents.all(), command_prefix=prefix)
        self.synced = False
        self.tree.add_command(Mints())
        self.tree.add_command(Aco())
        self.tree.add_command(Admin())
        self.tree.add_command(Payment())

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        print(f'{self.user} has connected to Discord!')
