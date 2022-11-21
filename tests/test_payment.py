import asyncio
import random

import pytest
import pytest_asyncio
from pytest_lazyfixture import lazy_fixture

from base_classes.errors import PaymentNotExist, WrongCheckoutsQuantity
from base_classes.member import Member
from base_classes.mint import Mint
from base_classes.payment import Payment, is_payment_exist, get_payment, add_checkout, check_checkouts_to_pay_correct, \
    get_unpaid_checkouts


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


class TestPayment:
    @pytest.mark.asyncio
    async def test_create_payment(self, mint, member):
        await Payment(mint_id=mint.id, mint_name=mint.name, member_id=member.id, amount_of_checkouts=10)
        assert await is_payment_exist(mint.id, member.id)

    @pytest.mark.asyncio
    async def test_get_payment(self, mint, member):
        await Payment(mint_id=mint.id, mint_name=mint.name, member_id=member.id, amount_of_checkouts=10)
        payment = await get_payment(mint.id, member.id)
        assert payment.mint_id == mint.id
        assert payment.mint_name == mint.name
        assert payment.member_id == member.id
        assert payment.amount_of_checkouts == 10

    @pytest.mark.asyncio
    async def test_get_payment_if_not_exist(self):
        with pytest.raises(PaymentNotExist):
            await get_payment("not exist name", -1)

    @pytest.mark.asyncio
    async def test_add_checkouts(self, mint, member):
        payment = await add_checkout(member, mint, 123)
        await asyncio.sleep(0.25)
        assert payment.mint_id == mint.id
        assert payment.mint_name == mint.name
        assert payment.member_id == member.id
        assert payment.amount_of_checkouts == 123

    @pytest.mark.asyncio
    async def test_add_checkouts_if_payment_exist(self, mint, member):
        await Payment(mint_id=mint.id, mint_name=mint.name, member_id=member.id, amount_of_checkouts=10)
        payment = await add_checkout(member, mint, 20)
        await asyncio.sleep(0.25)
        assert payment.amount_of_checkouts == 30

    @pytest.mark.asyncio
    async def test_checkouts_to_pay(self, mint, member):
        payment = await add_checkout(member, mint, 20)
        await asyncio.sleep(0.25)

        check_checkouts_to_pay_correct(10, payment)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_mint, test_member, wrong_amount",
                             [(lazy_fixture("mint"), lazy_fixture("member"), 30),
                              (lazy_fixture("mint"), lazy_fixture("member"), -1)])
    async def test_checkouts_to_pay_wrong_quantity(self, test_mint, test_member, wrong_amount):
        payment = await add_checkout(test_member, test_mint, 20)
        await asyncio.sleep(0.25)

        with pytest.raises(WrongCheckoutsQuantity):
            check_checkouts_to_pay_correct(wrong_amount, payment)

    @pytest.mark.asyncio
    async def test_get_unpaid_checkouts(self, mint, member):
        payment = await add_checkout(member, mint, 20)
        await asyncio.sleep(0.25)
        unpaid_checkouts = await get_unpaid_checkouts()
        assert unpaid_checkouts == [payment]
        payment.amount_of_checkouts = 0
        await asyncio.sleep(0.25)
        unpaid_checkouts = await get_unpaid_checkouts()
        assert unpaid_checkouts == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("attribute_to_change, value_to_set, test_mint, test_member",
                             [("amount_of_checkouts", 0, lazy_fixture("mint"), lazy_fixture("member")),
                              ("amount_of_checkouts", 10, lazy_fixture("mint"), lazy_fixture("member"))])
    async def test_update_attributes(self, attribute_to_change, value_to_set, test_mint, test_member):
        amount = random.randint(1, 100)
        payment = await Payment(mint_id=test_mint.id, mint_name=test_mint.name, member_id=test_member.id,
                                amount_of_checkouts=amount)
        payment.__setattr__(attribute_to_change, value_to_set)
        await asyncio.sleep(0.25)
        payment_from_database = await get_payment(test_mint.name, test_member.id)
        assert getattr(payment_from_database, attribute_to_change) == value_to_set
