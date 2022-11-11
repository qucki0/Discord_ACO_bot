import time

from base_classes.transaction import Transaction, get_all_transactions
from utilities.logging import get_logger
from .client import SolanaClient

logger = get_logger(__name__)
solana_client = SolanaClient()


async def check_valid_transaction(transaction_hash: str) -> tuple[str, float]:
    transaction_hash = get_transaction_hash_from_string(transaction_hash)
    if not is_hash_length_correct(transaction_hash):
        return "Wrong input.", -1
    if await is_hash_already_submitted(transaction_hash):
        return "This transaction already exist.", -1

    transaction_data = solana_client.get_transaction(transaction_hash)

    if not is_transaction_completed(transaction_data):
        return "Transaction isn't confirmed. Wait a bit and try again.", -1
    if is_transaction_completed_with_error(transaction_data):
        logger.error(f"Transaction error: {transaction_data}")  # to check what was wrong
        return "Something went wrong. Wait a bit and try again.", -1
    if not is_transaction_sol_transfer(transaction_data):
        return "This transaction isn't a $SOL transfer.", -1
    if not is_payment_address_correct(transaction_data):
        return "Wrong payment address.", -1
    balance_before_sending = transaction_data["result"]["meta"]["preBalances"][0]
    balance_after_sending = transaction_data["result"]["meta"]["postBalances"][0]
    transaction_fee = transaction_data["result"]["meta"]["fee"]
    sol_amount = (balance_before_sending - balance_after_sending - transaction_fee) / 1000000000
    return "Payment successful.", sol_amount


async def submit_transaction(tx_hash: str, member_id: int, release_data: str, checkouts_quantity: int) \
        -> tuple[str, float]:
    logger.info(
        f"Member {member_id} trying to submit {tx_hash=} for {release_data.upper()} to pay for {checkouts_quantity=}")
    tx_hash = get_transaction_hash_from_string(tx_hash)
    status, sol_amount = await check_valid_transaction(tx_hash)
    if sol_amount != -1:
        from base_classes.payment import get_payment
        payment = await get_payment(release_data, member_id)
        await Transaction(member_id=member_id, hash=tx_hash, amount=sol_amount, timestamp=int(time.time()))
        logger.info(
            f"Member {member_id} submitted {tx_hash=} for {release_data.upper()} to pay for {checkouts_quantity=}")
        payment.amount_of_checkouts = max(0, payment.amount_of_checkouts - checkouts_quantity)

    return status, sol_amount


def get_transaction_hash_from_string(transaction: str) -> str:
    if "/" in transaction:
        for possible_hash in transaction.split("/"):
            possible_hash = possible_hash.strip()
            if is_hash_length_correct(possible_hash):
                return possible_hash
    return transaction.strip()


def is_hash_length_correct(some_hash: str) -> bool:
    return 88 >= len(some_hash) >= 87


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
