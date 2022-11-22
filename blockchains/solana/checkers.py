def is_transaction_completed(transaction_data: dict) -> bool:
    return transaction_data["result"] is not None


def is_transaction_completed_with_error(transaction_data: dict) -> bool:
    return transaction_data["result"]["meta"]["err"] is not None


def is_transaction_sol_transfer(transaction_data: dict) -> bool:
    return len(transaction_data["result"]["meta"]["innerInstructions"]) == 0
