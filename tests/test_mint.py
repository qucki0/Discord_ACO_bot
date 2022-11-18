import asyncio
import random

import pytest

from base_classes.errors import MintNotExist, MintAlreadyExist
from base_classes.mint import Mint, is_mint_exist, get_mint_by_name, get_mint_by_id, check_mint_exist, \
    add_mint_to_mints_list, get_all_mints, get_actual_mints

BASE_NAME = "TEST NAME"


class TestMint:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("name, wallets_limit, timestamp, link", [(BASE_NAME, 123, None, None),
                                                                      (BASE_NAME, 123, 1234567890, None),
                                                                      (BASE_NAME, 123, None, "https://discord.com/"),
                                                                      (BASE_NAME, 123, 1234567890,
                                                                       "https://discord.com/")])
    async def test_create_mint(self, name, wallets_limit, timestamp, link):
        await Mint(name=name, wallets_limit=wallets_limit, timestamp=timestamp, link=link)
        assert await is_mint_exist(mint_name=name)
        mint = await get_mint_by_name(name)
        assert mint.name == name
        assert mint.wallets_limit == wallets_limit
        assert mint.timestamp == timestamp
        assert mint.link == link

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name, wallets_limit, timestamp, link", [(BASE_NAME, 123, None, None),
                                                                      (BASE_NAME, 123, 1234567890, None),
                                                                      (BASE_NAME, 123, None, "https://discord.com/"),
                                                                      (BASE_NAME, 123, 1234567890,
                                                                       "https://discord.com/")])
    async def test_get_mint(self, name, wallets_limit, timestamp, link):
        await Mint(name=name, wallets_limit=wallets_limit, timestamp=timestamp, link=link)
        mint = await get_mint_by_name(name)
        assert mint.name == name
        assert mint.wallets_limit == wallets_limit
        assert mint.timestamp == timestamp
        assert mint.link == link

    @pytest.mark.asyncio
    @pytest.mark.parametrize("attribute_to_change, value_to_set", [("name", "ANOTHER_TEST"), ("name", "small_test"),
                                                                   ("name", "New Name"), ("name", "другой язык"),
                                                                   ("timestamp", 1234567890), ("timestamp", None),
                                                                   ("link", "https://www.google.com/"), ("link", None),
                                                                   ("valid", False), ("checkouts", 0),
                                                                   ("checkouts", 123)])
    async def test_update_name(self, attribute_to_change, value_to_set):
        mint_name = f"{BASE_NAME}{random.randint(10 ** 0, 10 ** 20)}"
        mint = await Mint(name=mint_name)
        mint.__setattr__(attribute_to_change, value_to_set)
        await asyncio.sleep(0.2)
        mint_from_database = await get_mint_by_id(mint.id)
        assert getattr(mint_from_database, attribute_to_change) == value_to_set

    @pytest.mark.asyncio
    async def test_check_mint_exist(self):
        with pytest.raises(MintNotExist):
            await check_mint_exist(mint_name=BASE_NAME)
        with pytest.raises(MintNotExist):
            await check_mint_exist(mint_id=-1)

        mint = await Mint(name=BASE_NAME)
        await check_mint_exist(mint_name=BASE_NAME)
        await check_mint_exist(mint_id=mint.id)

    @pytest.mark.asyncio
    async def test_add_mint(self):
        with pytest.raises(AttributeError):
            await add_mint_to_mints_list(None, BASE_NAME)

    @pytest.mark.asyncio
    async def test_add_already_exist_mint(self):
        await Mint(name=BASE_NAME)
        with pytest.raises(MintAlreadyExist):
            await add_mint_to_mints_list(None, BASE_NAME)

    @pytest.mark.asyncio
    async def test_get_all_mints(self):
        assert await get_all_mints() == []
        first_mint = await Mint(name="first mint")
        assert await get_all_mints() == [first_mint]
        second_mint = await Mint(name="second mint")
        assert await get_all_mints() == [first_mint, second_mint]

    @pytest.mark.asyncio
    async def test_get_actual_mints(self):
        assert await get_actual_mints() == []
        first_mint = await Mint(name="first mint")
        assert await get_actual_mints() == [first_mint]
        second_mint = await Mint(name="second mint")
        assert await get_actual_mints() == [first_mint, second_mint]
        first_mint.valid = False
        await asyncio.sleep(0.2)
        assert await get_actual_mints() == [second_mint]
        second_mint.valid = False
        await asyncio.sleep(0.2)
        assert await get_actual_mints() == []
