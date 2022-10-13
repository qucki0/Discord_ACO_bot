from additions.all_data import solana_client, config, submitted_transactions
from solders.signature import Signature
import json


def check_valid_transaction(transaction_hash):
    transaction_hash = get_transaction_hash_from_string(transaction_hash)
    if not is_hash_length_correct(transaction_hash):
        return "Wrong input.", -1
    if is_hash_already_submitted(transaction_hash):
        return "This transaction already exist.", -1

    transaction_signature = Signature.from_string(transaction_hash)
    transaction_data_response = solana_client.get_transaction(transaction_signature)
    transaction_data = json.loads(transaction_data_response.to_json())

    if not is_transaction_completed(transaction_data):
        return "Transaction isn't completed. Wait a bit and try again.", -1
    if is_transaction_completed_with_error(transaction_data):
        print(transaction_data)  # to check what was wrong
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


def get_transaction_hash_from_string(transaction):
    if "/" in transaction:
        for possible_hash in transaction.split("/"):
            possible_hash = possible_hash.strip()
            if is_hash_length_correct(possible_hash):
                return possible_hash
    return transaction.strip()


def is_hash_length_correct(some_hash):
    return 88 >= len(some_hash) >= 87


def is_hash_already_submitted(transaction_hash):
    return any(tx.hash == transaction_hash for tx in submitted_transactions)


def is_transaction_completed(transaction_data):
    return transaction_data["result"] is not None


def is_transaction_completed_with_error(transaction_data):
    return transaction_data["result"]["meta"]["err"] is not None


def is_transaction_sol_transfer(transaction_data):
    return len(transaction_data["result"]["meta"]["innerInstructions"]) == 0


def is_payment_address_correct(transaction_data):
    return config.payment_wallet in transaction_data["result"]["transaction"]["message"]["accountKeys"]
