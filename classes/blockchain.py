import discord


class SubmitTransaction(discord.ui.Modal, title='Submit transaction'):
    tx_hash = discord.ui.TextInput(label='Transaction hash or solscan link', style=discord.TextStyle.short,
                                   placeholder="transaction", max_length=150, required=True)
    interaction = None

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.tx_hash = str(self.tx_hash)
        self.stop()
