import json

from solana.rpc.api import Client
from solders.signature import Signature

from base_classes.base import SingletonBase


class SolanaClient(Client, SingletonBase):
    def get_transaction(self, tx_hash: str, *args, **kwargs) -> dict:
        transaction_signature = Signature.from_string(tx_hash)
        transaction_data_response = super().get_transaction(transaction_signature, *args, **kwargs)
        return json.loads(transaction_data_response.to_json())
