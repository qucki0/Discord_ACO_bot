from additions.all_data import sql_client


def wallet(private_key: str) -> None:
    sql_client.delete_data("Wallets", {"private_key": private_key})
