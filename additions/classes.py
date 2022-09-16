import discord


class Drop:
    def __init__(self, id=None, timestamp=None, link=None, json_file=None):
        if json_file is None:
            self.id = id.strip()
            self.timestamp = timestamp
            self.link = link
            self.wallets = {}
            self.checkouts = 0
        else:
            self.id = json_file["id"]
            self.timestamp = json_file["timestamp"]
            self.link = json_file["link"]
            self.wallets = json_file["wallets"]
            self.checkouts = json_file["checkouts"]

    def get_as_dict(self):
        data = {"id": self.id,
                "timestamp": self.timestamp,
                "link": self.link,
                "wallets": self.wallets,
                "checkouts": self.checkouts}
        return data

    def get_drop_data(self):
        data = ""
        data += f"**{self.id}** "
        if self.timestamp is not None:
            data += f"<t:{self.timestamp}> "
        if self.link is not None:
            data += f"{self.link.strip()}"
        return data

    def get_wallets_by_id(self, member_id):
        if member_id in self.wallets:
            return self.wallets[member_id]

    def get_as_embed(self):
        description = ""
        if self.link is not None:
            description += f":green_circle:{self.link}\n\n"
        if self.timestamp is not None:
            description += f":clock10:Time: <t:{self.timestamp}>"

        embed = discord.Embed(title=f":bell:{self.id}", colour=discord.Colour.dark_grey(),
                              description=description)
        embed.set_footer(text="Take your ACO in ticket")
        return embed


class ACOMember:
    def __init__(self, member: discord.Member = None, json_file=None):
        if json_file is None:
            self.id = member.id
            self.name = member.name
            self.mints = {}
            self.payments = {}
        else:
            self.id = json_file["id"]
            self.name = json_file["name"]
            self.mints = json_file["mints"]
            self.payments = json_file["payments"]

    def get_as_dict(self):
        data = {"id": self.id,
                "name": self.name,
                "mints": self.mints,
                "payments": self.payments
                }
        return data
