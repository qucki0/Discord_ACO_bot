from abc import ABC

import web3.exceptions

from utilities.strings import get_transaction_hash_from_string
from .checkers import *
from .client import EthereumClientBase
from ..abstract_base import AbstractHandler


class EthereumHandlerBase(AbstractHandler, ABC):
    def __init__(self, rpc_link: str):
        self.client = EthereumClientBase(rpc_link)

    async def addition_checks(self, transaction_data: dict) -> tuple[str, float]:
        one_wei = 0.000000000000000001
        if is_gas_limit_correct(transaction_data):
            return "This transaction is not $ETH transfer", -1
        if not is_payment_amount_enough(transaction_data):
            return "Too small payment", -1
        eth_amount = round(int(transaction_data["value"]) * one_wei, 6)
        return "Payment successful.", eth_amount

    @staticmethod
    def is_private_key_correct(private_key: str) -> bool:
        return (len(private_key) == 66 and private_key.startswith("0x")) or (
                len(private_key) == 64 and not private_key.startswith("0x"))

    @staticmethod
    def is_transaction_hash_correct(transaction_hash: str) -> bool:
        return (len(transaction_hash) == 66 and transaction_hash.startswith("0x")) or (
                len(transaction_hash) == 64 and not transaction_hash.startswith("0x"))

    async def get_transaction(self, transaction_hash: str) -> dict | None:
        try:
            return await self.client.get_transaction(transaction_hash)
        except web3.exceptions.TransactionNotFound:
            return None

    def get_possible_transaction_hash_from_string(self, some_hash: str) -> str:
        return get_transaction_hash_from_string(some_hash, self.is_transaction_hash_correct)

    def is_payment_address_correct(self, transaction_data: dict) -> bool:
        return self.get_payment_wallet() == transaction_data["to"]
