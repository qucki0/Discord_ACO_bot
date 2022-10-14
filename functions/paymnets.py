from classes.classes import ACOMember, Drop


def add_checkouts(member: ACOMember, mint: Drop, amount_to_add: int) -> None:
    if mint.id not in member.payments:
        member.payments[mint.id] = {"amount_of_checkouts": amount_to_add,
                                    "unpaid_amount": amount_to_add}
    else:
        member.payments[mint.id]["amount_of_checkouts"] += amount_to_add
        member.payments[mint.id]["unpaid_amount"] += amount_to_add
    mint.checkouts += amount_to_add
