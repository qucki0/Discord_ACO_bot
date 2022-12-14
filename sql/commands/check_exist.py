import sql.commands
from ..client import SqlClient

sql_client = SqlClient()


async def member(member_id: int) -> bool:
    data = await sql_client.select_data("DiscordMembers", condition={"id": member_id})
    return bool(data)


async def mint(mint_id: int = None, mint_name: str = None) -> bool:
    condition = {}
    if mint_id is not None:
        condition["id"] = mint_id
    if mint_name is not None:
        condition["name"] = mint_name
    data = await sql_client.select_data("Mints", condition=condition)
    return bool(data)


async def transaction(transaction_hash: str) -> bool:
    data = await sql_client.select_data("Transactions", condition={"hash": transaction_hash})
    return bool(data)


async def wallet(private_key: str, mint_id: int) -> bool:
    data = await sql_client.select_data("Wallets", condition={"private_key": private_key, "mint_id": mint_id})
    return bool(data)


async def payment(mint_data: int | str, member_id: int) -> bool:
    mint_id = None
    match mint_data:
        case int():
            mint_id = mint_data
        case str():
            if await mint(mint_name=mint_data):
                mint_id = await sql.commands.get.mint_id_by_name(mint_data)
    data = await sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                        condition={"p.mint_id": mint_id, "p.member_id": member_id},
                                        join_tables=["Mints as m"],
                                        join_conditions=["p.mint_id = m.id"])
    return bool(data)
