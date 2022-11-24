def is_transaction_transfer(transaction_data: dict) -> bool:
    return "aptos_account::transfer" in transaction_data["payload"]["function"]
