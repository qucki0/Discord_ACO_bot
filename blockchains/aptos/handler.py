from setup import config
from utilities.logging import get_logger
from utilities.strings import get_transaction_hash_from_string
from .checkers import *
from .client import AptosClient
from ..abstract_base import AbstractHandler

logger = get_logger(__name__)


class AptosHandler(AbstractHandler):

    def __init__(self, rpc_link: str):
        self.client = AptosClient(rpc_link)

    async def addition_checks(self, transaction_data: dict) -> tuple[str, float]:
        if not is_transaction_transfer(transaction_data):
            return "Transaction is not $APT transfer", -1
        amount = int(transaction_data["payload"]["arguments"][1]) / 100000000
        return "Payment successful.", amount

    @staticmethod
    def is_private_key_correct(private_key: str) -> bool:
        return (len(private_key) == 66 and private_key.startswith("0x")) or (
                len(private_key) == 64 and not private_key.startswith("0x"))

    @staticmethod
    def is_transaction_hash_correct(transaction_hash: str) -> bool:
        return (len(transaction_hash) == 66 and transaction_hash.startswith("0x")) or (
                len(transaction_hash) == 64 and not transaction_hash.startswith("0x"))

    def get_possible_transaction_hash_from_string(self, some_hash: str) -> str:
        return get_transaction_hash_from_string(some_hash, self.is_private_key_correct)

    def get_payment_wallet(self) -> str:
        return config.blockchains.aptos.payment_wallet

    def is_payment_address_correct(self, transaction_data: dict) -> bool:
        return self.get_payment_wallet() in transaction_data["payload"]["arguments"]

    async def get_transaction(self, transaction_hash: str) -> dict | None:
        return await self.client.get_transaction(transaction_hash)

    @staticmethod
    def get_currency_symbol() -> str:
        return "APT"

    @staticmethod
    def get_block_scan_base_link() -> str:
        return "https://explorer.aptoslabs.com/txn/"
