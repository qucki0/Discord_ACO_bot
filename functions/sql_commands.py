from additions.all_data import sql_client
from classes.classes import ACOMember, Mint, Wallet, Payment
from classes.blockchain import Transaction


class Add:
    @staticmethod
    def member(member: ACOMember) -> None:
        sql_client.add_data("DiscordMembers", member.dict())

    @staticmethod
    def mint(mint: Mint) -> None:
        sql_client.add_data("Mints", mint.dict())

    @staticmethod
    def transaction(transaction: Transaction) -> None:
        sql_client.add_data("Transactions", transaction.dict())

    @staticmethod
    def wallet(wallet: Wallet) -> None:
        sql_client.add_data("Wallets", wallet.dict())

    @staticmethod
    def payment(payment: Payment) -> None:
        sql_client.add_data("Payments", payment.dict())


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
    def payment(mint_id: int, member_id: int, amount_of_checkouts: int) -> None:
        data_to_change = {}
        if amount_of_checkouts is not None:
            data_to_change["amount_of_checkouts"] = amount_of_checkouts
        sql_client.change_data("Payments", data_to_change, {"mint_id": mint_id, "member_id": member_id})


class Delete:
    @staticmethod
    def wallet(private_key: str) -> None:
        sql_client.delete_data("Wallets", {"private_key": private_key})


class Get:
    @staticmethod
    def member(member_id: int) -> ACOMember:
        data = sql_client.select_data("DiscordMembers", condition={"id": member_id})[0]
        return ACOMember.parse_obj(data)

    @staticmethod
    def mint(mint_id: int = None, mint_name: str = None) -> Mint:
        condition = {}
        if mint_id is not None:
            condition["id"] = mint_id
        if mint_name is not None:
            condition["name"] = mint_name
        data = sql_client.select_data("Mints", condition=condition)[0]
        return Mint.parse_obj(data)

    @staticmethod
    def transaction(transaction_hash: str) -> Transaction:
        data = sql_client.select_data("Transactions", condition={"hash": transaction_hash})[0]
        return Transaction.parse_obj(data)

    @staticmethod
    def wallet(private_key: str) -> Wallet:
        data = sql_client.select_data("Wallets", condition={"private_key": private_key})[0]
        return Wallet.parse_obj(data)

    @staticmethod
    def payment(mint_id: int, member_id: int) -> Payment:
        data = sql_client.select_data("Payments", condition={"mint_id": mint_id, "member_id": member_id})[0]
        return Payment.parse_obj(data)
