import discord


class SubmitTransaction(discord.ui.Modal, title='Submit transaction'):
    tx_hash = discord.ui.TextInput(label='Transaction hash or solscan link', style=discord.TextStyle.short,
                                   placeholder="transaction", max_length=150, required=True)
    interaction = None

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.tx_hash = str(self.tx_hash)
        self.stop()


class Transaction:
    def __init__(self, member: discord.Member = None, transaction_hash=None, amount=None, timestamp=None,
                 json_file=None):
        if json_file is None:
            self.member_id = member.id
            self.member_name = member.name
            self.hash = transaction_hash
            self.amount = amount
            self.timestamp = timestamp
        else:
            self.member_id = int(json_file["member_id"])
            self.member_name = json_file["member_name"]
            self.hash = json_file["hash"]
            self.amount = json_file["amount"]
            self.timestamp = int(json_file["timestamp"])

    def get_as_dict(self):
        data = {"member_id": self.member_id,
                "member_name": self.member_name,
                "hash": self.hash,
                "amount": self.amount,
                "timestamp": self.timestamp
                }
        return data
