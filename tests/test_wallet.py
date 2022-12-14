import asyncio
import random

import pytest
import pytest_asyncio
from pytest_lazyfixture import lazy_fixture

from base_classes.errors import WalletsNotExist
from base_classes.member import Member
from base_classes.mint import Mint, get_mint_by_id
from base_classes.wallet import create_wallet, AddWalletStatus, is_wallet_exists, delete_wallet, DeleteWalletStatus, \
    get_member_wallets_for_mint, Wallet, get_wallets_for_mint, add_wallets_to_mint, delete_wallets_from_mint

VALID_PRIVATE_KEY = "5ZdGUoEDLffbAFeN5552zYaapfv6Lpn8338xatFERG2dq4N9A6x8t35VrEDQLjU82YhL1rsL7njKUo6kthejVfgE"
ANOTHER_VALID_PRIVATE_KEY = "5Hdw8NtNANFTc2QZTA7qQhUTWNzxLi1UwT6b4vkZabTE89LvBkj3gdRzeTdDYEYZaKUwZeXS5zmNQXruLNPHE55x"


@pytest_asyncio.fixture(scope="function")
async def mint():
    mint_name = f"mint_name{random.randint(10 ** 0, 10 ** 20)}"
    m = await Mint(name=mint_name, wallets_limit=100)
    yield m


@pytest_asyncio.fixture(scope="function")
async def member():
    member_name = f"member_name{random.randint(10 ** 0, 10 ** 20)}"
    m = await Member(id=random.randint(10 ** 0, 10 ** 18), name=member_name)
    yield m


class TestWallets:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_member, test_mint, private_key, excepted_status", [(lazy_fixture("member"),
                                                                                       lazy_fixture("mint"),
                                                                                       VALID_PRIVATE_KEY,
                                                                                       AddWalletStatus.valid),
                                                                                      (lazy_fixture("member"),
                                                                                       lazy_fixture("mint"),
                                                                                       "Not private key",
                                                                                       AddWalletStatus.not_private_key)]
                             )
    async def test_create_wallet(self, test_member, test_mint, private_key, excepted_status):
        status = await create_wallet(private_key, test_mint, test_member.id)
        assert status == excepted_status

    @pytest.mark.asyncio
    async def test_check_wallet_exist(self, member, mint):
        status = await create_wallet(VALID_PRIVATE_KEY, mint, member.id)
        assert status == AddWalletStatus.valid
        assert await is_wallet_exists(VALID_PRIVATE_KEY, mint.id)

    @pytest.mark.asyncio
    async def test_delete_wallet(self, member, mint):
        add_status = await create_wallet(VALID_PRIVATE_KEY, mint, member.id)
        assert add_status == AddWalletStatus.valid
        delete_status = await delete_wallet(VALID_PRIVATE_KEY, mint.id)
        assert delete_status == DeleteWalletStatus.deleted

    @pytest.mark.asyncio
    async def test_get_wallets_for_mint(self, member, mint):
        await create_wallet(VALID_PRIVATE_KEY, mint, member.id)
        all_wallets = await get_wallets_for_mint(mint.id)
        first_wallet = Wallet(private_key=VALID_PRIVATE_KEY, mint_id=mint.id, member_id=member.id)
        assert all_wallets == [first_wallet]
        await create_wallet(ANOTHER_VALID_PRIVATE_KEY, mint, member.id)
        second_wallet = Wallet(private_key=ANOTHER_VALID_PRIVATE_KEY, mint_id=mint.id, member_id=member.id)
        all_wallets = await get_wallets_for_mint(mint.id)
        assert all_wallets == [first_wallet, second_wallet] or all_wallets == [second_wallet, first_wallet]

    @pytest.mark.asyncio
    async def test_get_member_wallet(self, member, mint):
        await create_wallet(VALID_PRIVATE_KEY, mint, member.id)
        all_wallets = await get_member_wallets_for_mint(member.id, mint.id)
        first_wallet = Wallet(private_key=VALID_PRIVATE_KEY, mint_id=mint.id, member_id=member.id)
        assert all_wallets == [first_wallet]
        await create_wallet(ANOTHER_VALID_PRIVATE_KEY, mint, member.id)
        second_wallet = Wallet(private_key=ANOTHER_VALID_PRIVATE_KEY, mint_id=mint.id, member_id=member.id)
        all_wallets = await get_member_wallets_for_mint(member.id, mint.id)
        assert all_wallets == [first_wallet, second_wallet] or all_wallets == [second_wallet, first_wallet]

    @pytest.mark.asyncio
    async def test_add_wallet_twice(self, member, mint):
        status = await create_wallet(VALID_PRIVATE_KEY, mint, member.id)
        assert status == AddWalletStatus.valid
        status = await create_wallet(VALID_PRIVATE_KEY, mint, member.id)
        assert status == AddWalletStatus.already_exist

    @pytest.mark.asyncio
    async def test_delete_not_existing_wallet(self):
        delete_status = await delete_wallet("not private key", -1)
        assert delete_status == DeleteWalletStatus.not_exist

    @pytest.mark.asyncio
    async def test_add_wallets_to_mint(self, member, mint):
        wallets_limit_before_adding = mint.wallets_limit
        wallets = [VALID_PRIVATE_KEY, ANOTHER_VALID_PRIVATE_KEY, "Not valid key"]
        not_private_keys, already_exist_keys, added_amount = await add_wallets_to_mint(wallets, mint, member.id)
        await asyncio.sleep(0.25)
        assert added_amount == 2
        assert len(not_private_keys) == 1
        assert not_private_keys[0] == "Not valid key"
        assert len(already_exist_keys) == 0
        assert len(await get_member_wallets_for_mint(member.id, mint.id)) == 2
        mint_from_database = await get_mint_by_id(mint.id)
        assert mint_from_database.wallets_limit == wallets_limit_before_adding - 2
        _, already_exist_keys, _ = await add_wallets_to_mint([VALID_PRIVATE_KEY], mint, member.id)
        assert len(already_exist_keys) == 1
        assert already_exist_keys[0] == VALID_PRIVATE_KEY
        assert len(await get_member_wallets_for_mint(member.id, mint.id)) == 2

    @pytest.mark.asyncio
    async def test_delete_all_wallets_from_mint(self, member, mint):
        wallets = [VALID_PRIVATE_KEY, ANOTHER_VALID_PRIVATE_KEY]
        await add_wallets_to_mint(wallets, mint, member.id)
        assert len(await get_member_wallets_for_mint(member.id, mint.id)) == 2
        deleted_amount = await delete_wallets_from_mint("all", mint, member.id)
        assert deleted_amount == 2
        with pytest.raises(WalletsNotExist):
            await get_member_wallets_for_mint(member.id, mint.id)
