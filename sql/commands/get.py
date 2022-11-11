import logging

from ..client import SqlClient

sql_client = SqlClient()

logger = logging.getLogger(__name__)


async def member(member_id: int) -> dict:
    data = await sql_client.select_data("DiscordMembers", condition={"id": member_id})
    return data[0]


async def mint(mint_id: int = None, mint_name: str = None) -> dict:
    condition = {}
    if mint_id is not None:
        condition["id"] = mint_id
    if mint_name is not None:
        condition["name"] = mint_name
    data = await sql_client.select_data("Mints", condition=condition)
    return data[0]


async def transaction(transaction_hash: str) -> dict:
    data = await sql_client.select_data("Transactions", condition={"hash": transaction_hash})
    return data[0]


async def wallet(private_key: str) -> dict:
    data = await sql_client.select_data("Wallets", condition={"private_key": private_key})
    return data[0]


async def payment(mint_data: int | str, member_id: int) -> dict:
    mint_id = None
    match mint_data:
        case int():
            mint_id = mint_data
        case str():
            mint_id = await mint_id_by_name(mint_data)
    data = await sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                        condition={"p.mint_id": mint_id, "p.member_id": member_id},
                                        join_tables=["Mints as m"],
                                        join_conditions=["p.mint_id = m.id"])
    return data[0]


async def actual_mints() -> list[dict]:
    logger.info("trying to get mints data")
    data = await sql_client.select_data("Mints", condition={"valid": 1})
    logger.info("got mints")
    return data


async def all_mints() -> list[dict]:
    data = await sql_client.select_data("Mints")
    return data


async def all_transactions() -> list[dict]:
    data = await sql_client.select_data("Transactions")
    return data


async def member_payments(member_id: int) -> list[dict]:
    data = await sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                        condition={"p.member_id": member_id}, join_tables=["Mints as m"],
                                        join_conditions=["p.mint_id = m.id"])
    return data


async def member_unpaid_payments(member_id: int) -> list[dict]:
    data = await sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                        condition={"p.member_id": member_id}, join_tables=["Mints as m"],
                                        join_conditions=["p.mint_id = m.id AND p.amount_of_checkouts > 0"])
    return data


async def mint_name_by_id(mint_id: int) -> str:
    data = await sql_client.select_data("Mints", data_to_select=["name"], condition={"id": mint_id})
    return data[0]["name"]


async def mint_id_by_name(mint_name: str) -> int:
    data = await sql_client.select_data("Mints", data_to_select=["id"], condition={"name": mint_name})
    return data[0]["id"]


async def unpaid_checkouts() -> list[dict]:
    data = await sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                        join_tables=["Mints as m"],
                                        join_conditions=["p.mint_id = m.id AND p.amount_of_checkouts > 0"])
    return data


async def member_wallets_for_mint(member_id: int, mint_id: int) -> list[dict]:
    data = await sql_client.select_data("Wallets", condition={"member_id": member_id, "mint_id": mint_id})
    return data


async def all_members() -> list[dict]:
    data = await sql_client.select_data("DiscordMembers")
    return data


async def wallets_for_mint(mint_data: int | str) -> list[dict]:
    mint_id = None
    match mint_data:
        case int():
            mint_id = mint_data
        case str():
            mint_id = await mint_id_by_name(mint_data)
    data = await sql_client.select_data("Wallets", condition={"mint_id": mint_id})
    return data
