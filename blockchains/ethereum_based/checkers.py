def is_gas_limit_correct(transaction_data: dict) -> bool:
    return int(transaction_data["gas"]) > 21000


def is_payment_amount_enough(transaction_data: dict):
    one_wei = 0.000000000000000001
    return int(transaction_data["value"]) * one_wei > 0.001
