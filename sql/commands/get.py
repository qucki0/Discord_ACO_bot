from ..client import SqlClient

sql_client = SqlClient()


def member(member_id: int) -> dict:
    data = sql_client.select_data("DiscordMembers", condition={"id": member_id})[0]
    return data


def mint(mint_id: int = None, mint_name: str = None) -> dict:
    condition = {}
    if mint_id is not None:
        condition["id"] = mint_id
    if mint_name is not None:
        condition["name"] = mint_name
    data = sql_client.select_data("Mints", condition=condition)[0]
    return data


def transaction(transaction_hash: str) -> dict:
    data = sql_client.select_data("Transactions", condition={"hash": transaction_hash})[0]
    return data


def wallet(private_key: str) -> dict:
    data = sql_client.select_data("Wallets", condition={"private_key": private_key})[0]
    return data


def payment(mint_data: int | str, member_id: int) -> dict:
    mint_id = None
    match mint_data:
        case int():
            mint_id = mint_data
        case str():
            mint_id = mint_id_by_name(mint_data)
    data = sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                  condition={"p.mint_id": mint_id, "p.member_id": member_id},
                                  join_tables=["Mints as m"],
                                  join_conditions=["p.mint_id = m.id"])[0]
    return data


def actual_mints() -> list[dict]:
    data = sql_client.select_data("Mints", condition={"valid": 1})
    return data


def all_mints() -> list[dict]:
    data = sql_client.select_data("Mints")
    return data


def all_transactions() -> list[dict]:
    data = sql_client.select_data("Transactions")
    return data


def member_payments(member_id: int) -> list[dict]:
    data = sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                  condition={"p.member_id": member_id}, join_tables=["Mints as m"],
                                  join_conditions=["p.mint_id = m.id"])
    return data


def member_unpaid_payments(member_id: int) -> list[dict]:
    data = sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                  condition={"p.member_id": member_id}, join_tables=["Mints as m"],
                                  join_conditions=["p.mint_id = m.id AND p.amount_of_checkouts > 0"])
    return data


def mint_name_by_id(mint_id: int) -> str:
    data = sql_client.select_data("Mints", data_to_select=["name"], condition={"id": mint_id})
    return data[0]["name"]


def mint_id_by_name(mint_name: str) -> int:
    data = sql_client.select_data("Mints", data_to_select=["id"], condition={"name": mint_name})
    return data[0]["id"]


def unpaid_checkouts() -> list[dict]:
    data = sql_client.select_data("Payments as p", data_to_select=["p.*, m.name as mint_name"],
                                  join_tables=["Mints as m"],
                                  join_conditions=["p.mint_id = m.id AND p.amount_of_checkouts > 0"])
    return data


def member_wallets_for_mint(member_id: int, mint_id: int) -> list[dict]:
    data = sql_client.select_data("Wallets", condition={"member_id": member_id, "mint_id": mint_id})
    return data


def all_members() -> list[dict]:
    data = sql_client.select_data("DiscordMembers")
    return data


def wallets_for_mint(mint_data: int | str) -> list[dict]:
    mint_id = None
    match mint_data:
        case int():
            mint_id = mint_data
        case str():
            mint_id = mint_id_by_name(mint_data)
    data = sql_client.select_data("Wallets", condition={"mint_id": mint_id})
    return data
