from ..client import SqlClient

sql_client = SqlClient()


def wallet(private_key: str) -> None:
    sql_client.delete_data("Wallets", {"private_key": private_key})
