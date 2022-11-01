import discord

import sql.commands
from base_classes.base import PropertyModel
from setup import config


class Mint(PropertyModel):
    id: int = None
    name_: str
    wallets_limit_: int
    timestamp_: int = None
    link_: str = None
    checkouts_: int = 0
    valid_: bool = True

    def __init__(self, **data):
        super().__init__(**data)

        if not sql.commands.check_exist.mint(mint_name=self.name):
            sql.commands.add.mint({key: self.dict()[key] for key in self.dict() if key != "id"})
        self.id = sql.commands.get.mint_id_by_name(self.name)

    def get_as_embed(self) -> discord.Embed:
        from my_discord import embeds
        return embeds.mint_data(self)

    def update_data(self, **kwargs):
        sql.commands.update.mint(self.id, **kwargs)

    @property
    def name(self):
        return self.name_

    @name.setter
    def name(self, value):
        pass

    def set_name(self, value):
        self.update_data(name=value)
        self.name_ = value

    @property
    def wallets_limit(self):
        return self.wallets_limit_

    @wallets_limit.setter
    def wallets_limit(self, value):
        pass

    def set_wallets_limit(self, value):
        self.update_data(wallets_limit=value)
        self.wallets_limit_ = value

    @property
    def timestamp(self):
        return self.timestamp_

    @timestamp.setter
    def timestamp(self, value):
        pass

    def set_timestamp(self, value):
        self.update_data(timestamp=value)
        self.timestamp_ = value

    @property
    def link(self):
        return self.link_

    @link.setter
    def link(self, value):
        pass

    def set_link(self, value):
        self.update_data(link=value)
        self.link_ = value

    @property
    def checkouts(self):
        return self.checkouts_

    @checkouts.setter
    def checkouts(self, value):
        pass

    def set_checkouts(self, value):
        self.update_data(checkouts=value)
        self.checkouts_ = value

    @property
    def valid(self):
        return self.valid_

    @valid.setter
    def valid(self, value):
        pass

    def set_valid(self, value):
        self.update_data(valid=value)
        self.valid_ = value

    class Config:
        attributes_to_change = ["name", "wallets_limit", "timestamp", "link", "checkouts", "valid"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


async def add_mint_to_mints_list(interaction: discord.Interaction, release_name: str, link: str, timestamp: int,
                                 wallets_limit: int = 10) -> None:
    if is_mint_exist(mint_name=release_name):
        await interaction.response.send_message(f"{release_name} already exist!", ephemeral=True)
    else:
        mint = Mint(name=release_name, link=link, timestamp=timestamp, wallets_limit=wallets_limit)
        await interaction.client.get_channel(config.alert_channel_id).send("New mint found", embed=mint.get_as_embed())
        await interaction.response.send_message(f"Added `{release_name}` to drop list!", ephemeral=True)


def is_mint_exist(mint_id=None, mint_name=None) -> bool:
    return sql.commands.check_exist.mint(mint_id=mint_id, mint_name=mint_name)


def get_mint_by_name(release_name: str) -> Mint | None:
    if not is_mint_exist(mint_name=release_name):
        return None
    return Mint.parse_obj(sql.commands.get.mint(mint_name=release_name))


def get_all_mints() -> list[Mint]:
    return [Mint.parse_obj(d) for d in sql.commands.get.all_mints()]


def get_actual_mints() -> list[Mint]:
    return [Mint.parse_obj(d) for d in sql.commands.get.actual_mints()]
