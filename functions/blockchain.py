from additions.all_data import solana_client, config, submitted_transactions


def check_valid_transaction(transaction_hash):
    if "/" in transaction_hash:
        for possible_hash in transaction_hash.split("/"):
            if len(possible_hash) == 88:
                transaction_hash = possible_hash

    if len(transaction_hash) != 88:
        return "Wrong input.", -1
    if any(tx.hash == transaction_hash for tx in submitted_transactions):
        return "This transaction already exist.", -1
    transaction_data = solana_client.get_transaction(transaction_hash.strip())
    if transaction_data["result"] is None:
        return "Transaction isn't completed. Wait a bit and try again.", -1
    if transaction_data["result"]["meta"]["err"] is not None:
        print(transaction_data)  # to check what was wrong
        return "Something went wrong. Wait a bit and try again.", -1
    if len(transaction_data["result"]["meta"]["innerInstructions"]) > 0:
        return "This transaction isn't a $SOL transfer.", -1
    if config.payment_wallet not in transaction_data["result"]["transaction"]["message"]["accountKeys"]:
        return "Wrong payment address.", -1
    balance_before_sending = transaction_data["result"]["meta"]["preBalances"][0]
    balance_after_sending = transaction_data["result"]["meta"]["postBalances"][0]
    transaction_fee = transaction_data["result"]["meta"]["fee"]
    sol_amount = (balance_before_sending - balance_after_sending - transaction_fee) / 1000000000
    return "Payment successful.", sol_amount
