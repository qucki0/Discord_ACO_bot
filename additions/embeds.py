import discord


class Embeds:
    @staticmethod
    def mint_data(mint_id, link, timestamp):
        description = ""
        if link is not None:
            description += f":green_circle:{link}\n\n"
        if timestamp is not None:
            description += f":clock10:Time: <t:{timestamp}>"
        embed = discord.Embed(title=f":bell:{mint_id}", colour=discord.Colour.dark_grey(), description=description)
        embed.set_footer(text="Take your ACO in ticket")
        return embed

    @staticmethod
    def unpaid_successes(member):
        description = ""
        for key in member.payments:
            if member.payments[key]["unpaid_amount"]:
                description += f"{key}, {member.payments[key]['unpaid_amount']} successes\n\n"
        if not description:
            description = "All your successes has already been paid"
        embed = discord.Embed(title=f"{member.name} Unpaid Successes", colour=discord.Colour.red(),
                              description=description)
        return embed

    @staticmethod
    def help():
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
                                       "*amount_to_pay:* **«Количество SOL»**")
        return mints_embed, wallets_embed, payments_embed

    @staticmethod
    def success(member_name, release_name, amount_of_checkouts):
        success_embed = discord.Embed(title=f"{member_name} success!", colour=discord.Colour.from_str("#58b9ff"))
        success_embed.add_field(name="__**Release:**__", value=release_name, inline=False)
        success_embed.add_field(name="__**Checkouts:**__", value=str(amount_of_checkouts), inline=False)
        icon_url = "https://cdn.discordapp.com/avatars/374449765695356929/fb9059b6d3d2b7c4af6424828cce27b1.webp?size=96"
        success_embed.set_footer(text="GangHujo#3839 ACO",
                                 icon_url=icon_url)
        return success_embed
