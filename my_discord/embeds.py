import discord

from base_classes.member import Member
from base_classes.mint import Mint
from base_classes.payment import get_member_unpaid_payments
from blockchains.solana.classes import Transaction
from setup import config


def mint_data(mint: Mint) -> discord.Embed:
    embed = discord.Embed(title=f":bell:{mint.name}", colour=discord.Colour.red())
    if mint.link is not None:
        embed.add_field(name="Link:", value=mint.link)
    if mint.timestamp is not None:
        embed.add_field(name="Time:", value=f"<t:{mint.timestamp}>")
    if mint.wallets_limit is not None:
        embed.add_field(name="Spots left:", value=str(mint.wallets_limit), inline=False)
    embed.set_footer(text="Take your ACO in ticket")
    return embed


def unpaid_successes(member: Member) -> discord.Embed:
    if member is None:
        return discord.Embed(title=f"New member unpaid successes", colour=discord.Colour.red(),
                             description="Nothing to see here;)")
    embed = discord.Embed(title=f"{member.name} Unpaid Successes", colour=discord.Colour.red())
    payments = get_member_unpaid_payments(member.id)
    for i, payment in enumerate(payments):
        embed.add_field(name=f"{payment.mint_name}:", value=payment.amount_of_checkouts, inline=i % 4 != 3)
    return embed


def help_embeds() -> tuple[discord.Embed, discord.Embed, discord.Embed, discord.Embed]:
    mints_embed = discord.Embed(title="/mints", colour=discord.Colour.red())
    mints_embed.add_field(name="**/mints get-all** - список минтов на сегодня, обновляется каждый день.",
                          value="Параметры не требуются")
    mints_embed.add_field(name="**/mints request** - если мы упустили какой-то проект, то используйте эту команду.",
                          value="*release_name:* **«Название релиза»**\n"
                                "*link:* **«Ссылка на проект»** *(необязательно)*"
                                "\n*mint_time:* **«Таймстамп минта»** *(необязательно)*")
    wallets_embed = discord.Embed(title="/wallets", colour=discord.Colour.red())
    wallets_embed.add_field(name="**/wallets send** - отправить кошельки на минт.",
                            value="*release_name:* **«Название релиза»** *(название из /mints get-all)*")
    wallets_embed.add_field(name="**/wallets check** - посмотреть список добавленных кошельков.",
                            value="*release_name:* **«Название релиза»**")
    wallets_embed.add_field(name="/wallets delete - удаление добавленных кошельков.",
                            value="*release_name:* **«Название релиза»**\n"
                                  "*wallets:* **«ключ1 ключ2 ключ3»** *(приватные ключи кошельков через пробел)*"
                                  " или **«all»** *(выбор всех кошельков)*")
    payments_embed = discord.Embed(title="/payments", colour=discord.Colour.red())
    payments_embed.add_field(name="/payment check-payments - посмотреть список неоплаченных чекаутов.",
                             value="Параметры не требуются")
    payments_embed.add_field(name="**/payment pay** - оплатить успешные чекауты.",
                             value="*release_name:* **«Название релиза»**\n"
                                   "*checkouts_quantity:* **«Количество чекаутов для оплаты»**")
    wallet_manager_embed = discord.Embed(title="/wallet-manager", colour=discord.Colour.red())
    wallet_manager_embed.add_field(name="/wallet-manager download - получить ссылку на скачивание валлет менеджера.",
                                   value="Параметры не требуются")
    wallet_manager_embed.add_field(name="/wallet-manager get-key - получить ключ для валлет менеджера.",
                                   value="Параметры не требуются")
    set_footer(wallet_manager_embed)
    return mints_embed, wallets_embed, payments_embed, wallet_manager_embed


def success(member_name: str, release_name: str, amount_of_checkouts: int) -> discord.Embed:
    success_embed = discord.Embed(title=f"{member_name} success!", colour=discord.Colour.red())
    success_embed.add_field(name="__**Release:**__", value=release_name, inline=False)
    success_embed.add_field(name="__**Checkouts:**__", value=str(amount_of_checkouts), inline=False)
    set_footer(success_embed)
    return success_embed


def wallet_manager_download() -> discord.Embed:
    link = config.wallet_manager_link
    download_embed = discord.Embed(title=f"Wallet Manager link:", colour=discord.Colour.red(),
                                   description=f"[Download]({link})")
    set_footer(download_embed)
    return download_embed


def wallet_manager_login_data(nickname: str, key: str, timestamp: int) -> discord.Embed:
    login_data = discord.Embed(title="You credentials:", colour=discord.Colour.red())
    login_data.add_field(name="nickname:",
                         value=f"`{nickname}`")
    login_data.add_field(name="key:",
                         value=f"`{key}`")
    login_data.add_field(name="Expire in:",
                         value=f"<t:{timestamp}:R>",
                         inline=False)
    set_footer(login_data)
    return login_data


def transaction_status(status: str, sol_amount: float, member: Member, transaction_hash: str) \
        -> tuple[discord.Embed, ...]:
    url = "https://solscan.io/tx/" + transaction_hash.replace(" ", "_").replace("\n", "__")
    transaction_status_embed = discord.Embed(title="Transaction details", colour=discord.Colour.red(), url=url)
    transaction_status_embed.add_field(name="Status:", value=status, inline=False)
    if sol_amount != -1:
        transaction_status_embed.add_field(name="Amount:", value=sol_amount, inline=False)
        return transaction_status_embed, unpaid_successes(member)
    return transaction_status_embed,


def transaction_info(transaction: Transaction) -> discord.Embed:
    url = "https://solscan.io/tx/" + transaction.hash
    transaction_data_embed = discord.Embed(title="Transaction info", colour=discord.Colour.red(), url=url)
    transaction_data_embed.add_field(name="Submitted by:", value=f"<@{transaction.member_id}>")
    transaction_data_embed.add_field(name="Submission date:", value=f"<t:{transaction.timestamp}>")
    transaction_data_embed.add_field(name="Amount:", value=f"{transaction.amount} $SOL", inline=False)
    return transaction_data_embed


def mint_info(mint: Mint) -> discord.Embed:
    mint_info_embed = discord.Embed(title=f"{mint.name}", colour=discord.Colour.red())
    mint_info_embed.add_field(name="Checkouts:", value=f"{mint.checkouts}")
    return mint_info_embed


def tickets_menu() -> discord.Embed:
    tickets_menu_embed = discord.Embed(title="Support",
                                       description="Create a ticket using the button below",
                                       colour=discord.Colour.red())
    set_footer(tickets_menu_embed)
    return tickets_menu_embed


def ticket() -> discord.Embed:
    ticket_embed = discord.Embed(description="Ticket menu",
                                 colour=discord.Colour.red())
    return ticket_embed


def set_footer(embed: discord.Embed) -> None:
    icon_url = "https://cdn.discordapp.com/icons/838092056060624986/289b99bd777b929251cdbbd26bec96bd.webp"
    embed.set_footer(text="Aco Cola",
                     icon_url=icon_url)
