import discord

from additions import all_data


def mint_data(mint_id, link, timestamp, wallets_limit):
    embed = discord.Embed(title=f":bell:{mint_id}", colour=discord.Colour.dark_grey())
    if link is not None:
        embed.add_field(name="Link:", value=link)
    if timestamp is not None:
        embed.add_field(name="Time:", value=f"<t:{timestamp}>")
    if wallets_limit is not None:
        embed.add_field(name="Spots left:", value=str(wallets_limit), inline=False)
    embed.set_footer(text="Take your ACO in ticket")
    return embed


def unpaid_successes(member):
    if member is None:
        return discord.Embed(title=f"New member unpaid successes", colour=discord.Colour.red(),
                             description="Nothing to see here;)")
    embed = discord.Embed(title=f"{member.name} Unpaid Successes", colour=discord.Colour.red())
    for i, key in enumerate(member.payments):
        if member.payments[key]["unpaid_amount"]:
            embed.add_field(name=f"{key}:", value=member.payments[key]['unpaid_amount'], inline=i % 4 != 3)
    return embed


def help_embeds():
    mints_embed = discord.Embed(title="/mints", colour=discord.Colour.red())
    mints_embed.add_field(name="**/mints get-all** - список минтов на сегодня, будет обновляться каждый день.",
                          value="Параметры не требуются.")
    mints_embed.add_field(name="**/mints request** - если мы упустили какой-то проект, то используйте эту команду.",
                          value="*release_id:* **«Название релиза»**\n"
                                "*link:* **«Ссылка на проект»** *(необязательно)*"
                                "\n*mint_time:* **«Время минта»** *(необязательно)*")
    wallets_embed = discord.Embed(title="/wallets", colour=discord.Colour.red())
    wallets_embed.add_field(name="**/wallets send** - отправить кошельки на минт.",
                            value="*release_id:* **«Название релиза»** *(название из /mints get-all)*\n"
                                  "*wallets:* **«ключ1, ключ2, ключ3»**"
                                  " *(приватные ключи кошельков через запятую)* ")
    wallets_embed.add_field(name="**/wallets check** - просмотр добавленных кошельков.",
                            value="*release_id:* **«Название релиза»**")
    wallets_embed.add_field(name="/wallets delete - удаление добавленных кошельков.",
                            value="*release_id:* **«Название релиза»**\n"
                                  "*wallets:* **«ключ1, ключ2, ключ3»** *(приватные ключи кошельков через запятую)*"
                                  " или **«all»** *(выбор всех кошельков)*")
    payments_embed = discord.Embed(title="/payments", colour=discord.Colour.red())
    payments_embed.add_field(name="/payment check-payments - просмотр неоплаченных чекаутов.",
                             value="Параметры не требуются.")
    payments_embed.add_field(name="**/payment pay** - оплата за ваши чекауты.",
                             value="*release_name:* **«Название релиза»**\n"
                                   "*amount_to_pay:* **«Количество SOL»**\n"
                                   "*checkouts_quantity:* **«Количество чекаутов для оплаты»**")
    set_footer(payments_embed)
    return mints_embed, wallets_embed, payments_embed


def success(member_name, release_name, amount_of_checkouts):
    success_embed = discord.Embed(title=f"{member_name} success!", colour=discord.Colour.from_str("#58b9ff"))
    success_embed.add_field(name="__**Release:**__", value=release_name, inline=False)
    success_embed.add_field(name="__**Checkouts:**__", value=str(amount_of_checkouts), inline=False)
    set_footer(success_embed)
    return success_embed


def wallet_manager_download():
    link = all_data.config.wallet_manager_link
    download_embed = discord.Embed(title=f"Wallet Manager link:", colour=discord.Colour.red(),
                                   description=f"[Download]({link})")
    set_footer(download_embed)
    return download_embed


def wallet_manager_login_data(nickname, key, timestamp):
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


def set_footer(embed):
    icon_url = "https://cdn.discordapp.com/icons/838092056060624986/289b99bd777b929251cdbbd26bec96bd.webp"
    embed.set_footer(text="Aco Cola",
                     icon_url=icon_url)
