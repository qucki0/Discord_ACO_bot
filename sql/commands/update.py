from setup import sql_client


def member(member_id: int, name: str = None, ticket_id: int = -1) -> None:
    data_to_change = {}
    if name is not None:
        data_to_change["name"] = name
    if ticket_id != -1:
        data_to_change["ticket_id"] = ticket_id
    sql_client.change_data("DiscordMembers", data_to_change, {"id": member_id})


def mint(mint_id: int, name: str = None, timestamp: int = None, link: str = None, wallets_limit: int = None,
         checkouts: int = None, valid: int = None) -> None:
    temp_dict = {"name": name, "timestamp": timestamp, "link": link, "wallets_limit": wallets_limit,
                 "checkouts": checkouts, "valid": valid}
    data_to_change = {key: temp_dict[key] for key in temp_dict if temp_dict[key] is not None}
    sql_client.change_data("Mints", data_to_change, {"id": mint_id})


def payment(mint_id: int, member_id: int, amount_of_checkouts: int) -> None:
    data_to_change = {}
    if amount_of_checkouts is not None:
        data_to_change["amount_of_checkouts"] = amount_of_checkouts
    sql_client.change_data("Payments", data_to_change, {"mint_id": mint_id, "member_id": member_id})
