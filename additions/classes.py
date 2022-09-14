import discord


class Drop:
    def __init__(self, name=None, timestamp=None, link=None, json_file=None):
        if json_file is None:
            self.name = name.strip()
            self.timestamp = timestamp
            self.link = link
            self.wallets = {}
        else:
            self.name = json_file["name"]
            self.timestamp = json_file["timestamp"]
            self.link = json_file["link"]
            self.wallets = json_file["wallets"]

    def get_as_dict(self):
        data = {"name": self.name,
                "timestamp": self.timestamp,
                "link": self.link,
                "wallets": self.wallets}
        return data

    def get_drop_data(self):
        data = ""
        data += f"**{self.name}** "
        if self.timestamp is not None:
            data += f"<t:{self.timestamp}> "
        if self.link is not None:
            data += f"{self.link.strip()}"
        return data

    def get_wallets_by_name(self, member_name):
        if member_name in self.wallets:
            return self.wallets[member_name]

    def get_as_embed(self):
        description = ""
        if self.link is not None:
            description += f":green_circle:{self.link}\n\n"
        if self.timestamp is not None:
            description += f":clock10:Time: <t:{self.timestamp}>"

        embed = discord.Embed(title=f":bell:{self.name}", colour=discord.Colour.dark_grey(),
                              description=description)
        embed.set_footer(text="Take your ACO in ticket")
        return embed


class ACOMember:
    def __init__(self, member: discord.Member):
        self.member = member
        self.mints = {}
