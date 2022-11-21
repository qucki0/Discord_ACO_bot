from base_classes.transaction import get_all_transactions


async def is_hash_already_submitted(transaction_hash: str) -> bool:
    submitted_transactions = await get_all_transactions()
    return any(tx.hash == transaction_hash for tx in submitted_transactions)


def is_transaction_completed(transaction_data: dict) -> bool:
    return transaction_data["result"] is not None


def is_transaction_completed_with_error(transaction_data: dict) -> bool:
    return transaction_data["result"]["meta"]["err"] is not None


def is_transaction_sol_transfer(transaction_data: dict) -> bool:
    return len(transaction_data["result"]["meta"]["innerInstructions"]) == 0


def is_payment_address_correct(transaction_data: dict) -> bool:
    from setup import config
    return config.blockchains.solana.payment_wallet in transaction_data["result"]["transaction"]["message"][
        "accountKeys"]
