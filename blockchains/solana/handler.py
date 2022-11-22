from setup import config
from utilities.logging import get_logger
from utilities.strings import get_transaction_hash_from_string
from .checkers import *
from .client import SolanaClient
from ..abstract_base import AbstractHandler

logger = get_logger(__name__)


class SolanaHandler(AbstractHandler):

    def __init__(self, rpc_link: str):
        self.client = SolanaClient(rpc_link)
        super().__init__()

    async def addition_checks(self, transaction_data: dict) -> tuple[str, int]:
        if not is_transaction_completed(transaction_data):
            return "Transaction isn't confirmed. Wait a bit and try again.", -1
        if is_transaction_completed_with_error(transaction_data):
            logger.error(f"Transaction error: {transaction_data}")  # to check what was wrong
            return "Something went wrong. Wait a bit and try again.", -1
        if not is_transaction_sol_transfer(transaction_data):
            return "This transaction isn't a $SOL transfer.", -1
        balance_before_sending = transaction_data["result"]["meta"]["preBalances"][0]
        balance_after_sending = transaction_data["result"]["meta"]["postBalances"][0]
        transaction_fee = transaction_data["result"]["meta"]["fee"]
        sol_amount = (balance_before_sending - balance_after_sending - transaction_fee) / 1000000000
        return "Payment successful.", sol_amount

    @staticmethod
    def is_private_key_correct(private_key: str) -> bool:
        return 88 >= len(private_key) >= 87

    @staticmethod
    def is_transaction_hash_correct(transaction_hash: str) -> bool:
        return 88 >= len(transaction_hash) >= 87

    def get_possible_transaction_hash_from_string(self, some_hash: str) -> str:
        return get_transaction_hash_from_string(some_hash, self.is_private_key_correct)

    def get_payment_wallet(self) -> str:
        return config.blockchains.solana.payment_wallet

    def is_payment_address_correct(self, transaction_data: dict) -> bool:
        return self.get_payment_wallet() in transaction_data["result"]["transaction"]["message"]["accountKeys"]

    async def get_transaction(self, transaction_hash: str) -> dict | None:
        return self.client.get_transaction(transaction_hash)
