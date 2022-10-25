from additions.all_data import sql_client


class Add:
    @staticmethod
    def member(member_id: int, member_name: str) -> None:
        data_to_add = {"id": member_id,
                       "name": member_name}
        sql_client.add_data("DiscordMembers", data_to_add)

    @staticmethod
    def mint(mint_name: str, wallets_limit: int, timestamp: int = None, link: str = None) -> None:
        data_to_add = {"name": mint_name,
                       "wallets_limit": wallets_limit,
                       "timestamp": timestamp,
                       "link": link}
        sql_client.add_data("Mints", data_to_add)

    @staticmethod
    def transaction(transaction_hash: str, member_id: int, amount: float, timestamp: int) -> None:
        data_to_add = {
            "hash": transaction_hash,
            "member_id": member_id,
            "amount": amount,
            "timestamp": timestamp
        }
        sql_client.add_data("Transactions", data_to_add)

    @staticmethod
    def wallet(private_key: str, mint_id: int, member_id: int) -> None:
        data_to_add = {
            "private_key": private_key,
            "mint_id": mint_id,
            "member_id": member_id
        }
        sql_client.add_data("Wallets", data_to_add)

    @staticmethod
    def payment(mint_id: int, member_id: int, amount_of_checkouts: int) -> None:
        data_to_add = {
            "mint_id": mint_id,
            "member_id": member_id,
            "amount_of_checkouts": amount_of_checkouts
        }
        sql_client.add_data("Payments", data_to_add)


class Change:
    @staticmethod
    def member(member_id: int, name: str = None, ticket_id: int = -1) -> None:
        data_to_change = {}
        if name is not None:
            data_to_change["name"] = name
        if ticket_id != -1:
            data_to_change["ticket_id"] = ticket_id
        sql_client.change_data("DiscordMembers", data_to_change, {"id": member_id})

    @staticmethod
    def mint(mint_id: int, name: str = None, timestamp: int = None, link: str = None, wallets_limit: int = None,
             checkouts: int = None, valid: int = None) -> None:
        temp_dict = {"name": name, "timestamp": timestamp, "link": link, "wallets_limit": wallets_limit,
                     "checkouts": checkouts, "valid": valid}
        data_to_change = {key: temp_dict[key] for key in temp_dict if temp_dict[key] is not None}
        sql_client.change_data("Mints", data_to_change, {"id": mint_id})

    @staticmethod
    def payment(mint_id: str, member_id: int, amount_of_checkouts: int) -> None:
        data_to_change = {}
        if amount_of_checkouts is not None:
            data_to_change["amount_of_checkouts"] = amount_of_checkouts
        sql_client.change_data("Payments", data_to_change, {"mint_id": mint_id, "member_id": member_id})


class Delete:
    @staticmethod
    def wallet(private_key: str) -> None:
        sql_client.delete_data("Wallets", {"private_key": private_key})
