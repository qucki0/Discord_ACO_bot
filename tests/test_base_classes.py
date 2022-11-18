import asyncio
import random

import pytest

from base_classes.member import Member, is_member_exists, get_member_by_id, update_member, get_member_name_by_id

BASE_MEMBER_ID = 123456789123456789
BASE_NAME = "TEST NAME"


class TestMember:
    @pytest.mark.asyncio
    async def test_create_member(self):
        await Member(id=BASE_MEMBER_ID, name=BASE_NAME)
        assert await is_member_exists(BASE_MEMBER_ID)
        member = await get_member_by_id(BASE_MEMBER_ID)
        assert member.id == BASE_MEMBER_ID
        assert member.name == BASE_NAME

    @pytest.mark.asyncio
    async def test_get_member(self):
        await Member(id=BASE_MEMBER_ID, name=BASE_NAME)
        member = await get_member_by_id(BASE_MEMBER_ID)
        assert member.id == BASE_MEMBER_ID
        assert member.name == BASE_NAME

    @pytest.mark.asyncio
    @pytest.mark.parametrize("attribute_to_change, value_to_set", [("name", "NEW_TEST_NAME"), ("ticket_id", 987654321)])
    async def test_update_info(self, attribute_to_change: str, value_to_set: int | str | None):
        member_id = random.randint(10 ** 17, 10 ** 18)
        member = await Member(id=member_id, name=BASE_NAME)
        await update_member(member, **{attribute_to_change: value_to_set})
        member_from_database = await get_member_by_id(member_id)
        assert getattr(member_from_database, attribute_to_change) == value_to_set

    @pytest.mark.asyncio
    @pytest.mark.parametrize("new_name", ["ANOTHER_TEST", "small_test", "New Name", "другой язык",
                                          "\u4efb\u4f55\u5b57\u7b26\u4e32\u5728\u4e2d\u570b", "emoji_test🙃",
                                          "", "very  long  test nickname same as max nickname length on discord"])
    async def test_update_name(self, new_name: str):
        member_id = random.randint(10 ** 17, 10 ** 18)
        member = await Member(id=member_id, name=BASE_NAME)
        member.name = new_name
        await asyncio.sleep(0.2)
        member_from_database = await get_member_by_id(member_id)
        assert member_from_database.name == new_name

    @pytest.mark.asyncio
    @pytest.mark.parametrize("new_ticket_ids", [(1234,), (1234, None)])
    async def test_update_ticket_id(self, new_ticket_ids: list[int]):
        member_id = random.randint(10 ** 17, 10 ** 18)
        member = await Member(id=member_id, name=BASE_NAME)
        for new_ticket_id in new_ticket_ids:
            member.ticket_id = new_ticket_id
            await asyncio.sleep(0.2)
            member_from_database = await get_member_by_id(member_id)
            assert member_from_database.ticket_id == new_ticket_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name_to_test, excepted_result", [("some-test-name", "some-test-name"),
                                                               ("another-test🙃", "another-test")])
    async def test_get_member_name(self, name_to_test, excepted_result):
        member_id = random.randint(10 ** 17, 10 ** 18)
        await Member(id=member_id, name=name_to_test)
        member_name = await get_member_name_by_id(member_id)
        assert member_name == excepted_result

    @pytest.mark.asyncio
    async def test_get_if_not_exist(self):
        with pytest.raises(IndexError):
            await get_member_by_id(BASE_MEMBER_ID)
