import discord

import sql.commands
from base_classes.base import PropertyModel, AsyncObject
from utilities.logging import get_logger

logger = get_logger(__name__)


class Mint(PropertyModel, AsyncObject):
    id: int = None
    name_: str
    wallets_limit_: int
    timestamp_: int = None
    link_: str = None
    checkouts_: int = 0
    valid_: bool = True

    async def __ainit__(self, *args, **kwargs):
        if not await is_mint_exist(mint_name=self.name):
            await create_mint(self)
        if self.id is None:
            self.id = (await get_mint_by_name(self.name)).id

    def get_as_embed(self) -> discord.Embed:
        from my_discord import embeds
        return embeds.mint_data(self)

    @property
    def name(self):
        return self.name_

    @name.setter
    def name(self, value):
        pass

    async def set_name(self, value):
        await update_mint(self, name=value)
        self.name_ = value

    @property
    def wallets_limit(self):
        return self.wallets_limit_

    @wallets_limit.setter
    def wallets_limit(self, value):
        pass

    async def set_wallets_limit(self, value):
        await update_mint(self, wallets_limit=value)
        self.wallets_limit_ = value

    @property
    def timestamp(self):
        return self.timestamp_

    @timestamp.setter
    def timestamp(self, value):
        pass

    async def set_timestamp(self, value):
        await update_mint(self, timestamp=value)
        self.timestamp_ = value

    @property
    def link(self):
        return self.link_

    @link.setter
    def link(self, value):
        pass

    async def set_link(self, value):
        await update_mint(self, link=value)
        self.link_ = value

    @property
    def checkouts(self):
        return self.checkouts_

    @checkouts.setter
    def checkouts(self, value):
        pass

    async def set_checkouts(self, value):
        await update_mint(self, checkouts=value)
        self.checkouts_ = value

    @property
    def valid(self):
        return self.valid_

    @valid.setter
    def valid(self, value):
        pass

    async def set_valid(self, value):
        await update_mint(self, valid=value)
        self.valid_ = value

    class Config:
        attributes_to_change = ["name", "wallets_limit", "timestamp", "link", "checkouts", "valid"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


async def create_mint(mint: Mint) -> None:
    await sql.commands.add.mint({key: mint.dict()[key] for key in mint.dict() if key != "id"})


async def update_mint(mint: Mint, **kwargs) -> None:
    await sql.commands.update.mint(mint.id, **kwargs)


async def is_mint_exist(mint_id=None, mint_name=None) -> bool:
    return await sql.commands.check_exist.mint(mint_id=mint_id, mint_name=mint_name)


async def get_mint_by_name(release_name: str) -> Mint | None:
    if not await is_mint_exist(mint_name=release_name):
        return None
    return Mint.parse_obj(await sql.commands.get.mint(mint_name=release_name))


async def get_all_mints() -> list[Mint]:
    return [Mint.parse_obj(d) for d in await sql.commands.get.all_mints()]


async def get_actual_mints() -> list[Mint]:
    return [Mint.parse_obj(d) for d in await sql.commands.get.actual_mints()]


async def add_mint_to_mints_list(interaction: discord.Interaction, release_name: str, link: str, timestamp: int,
                                 wallets_limit: int = 10) -> None:
    if await is_mint_exist(mint_name=release_name):
        await interaction.response.send_message(f"{release_name} already exist!", ephemeral=True)
        return
    logger.debug(f"Adding mint {release_name=}, {link=}, {timestamp=}, {wallets_limit}")
    mint = await Mint(name=release_name, link=link, timestamp=timestamp, wallets_limit=wallets_limit)

    from setup import config
    await interaction.client.get_channel(config.alert_channel_id).send("New mint found", embed=mint.get_as_embed())
    await interaction.response.send_message(f"Added `{release_name}` to drop list!", ephemeral=True)
