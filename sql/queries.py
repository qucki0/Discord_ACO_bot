create_table_discord_members = """
    CREATE TABLE IF NOT EXISTS `DiscordMembers` (
        `id` BIGINT NOT NULL,
        `name` VARCHAR(255) NOT NULL,
        `ticket_id` BIGINT,
        PRIMARY KEY (`id`)
    );
    """
create_table_mints = """
    CREATE TABLE IF NOT EXISTS `Mints` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `name` VARCHAR(255) NOT NULL,
        `timestamp` BIGINT,
        `link` VARCHAR(255),
        `wallets_limit` INT NOT NULL,
        `checkouts` INT NOT NULL DEFAULT '0',
        `valid` BOOLEAN NOT NULL DEFAULT true,
        PRIMARY KEY (`id`, `name`)
    );
    """
create_table_wallets = """
    CREATE TABLE IF NOT EXISTS `Wallets` (
        `private_key` VARCHAR(255) NOT NULL,
        `mint_id` INT NOT NULL,
        `member_id` BIGINT NOT NULL,
        PRIMARY KEY (`private_key`, `mint_id`),
        CONSTRAINT `Wallets_fk0` FOREIGN KEY (`mint_id`) REFERENCES `Mints`(`id`),
        CONSTRAINT `Wallets_fk1` FOREIGN KEY (`member_id`) REFERENCES `DiscordMembers`(`id`)
    );
    """
create_table_transactions = """
    CREATE TABLE IF NOT EXISTS `Transactions` (
        `hash` VARCHAR(255) NOT NULL,
        `member_id` BIGINT NOT NULL,
        `amount` FLOAT NOT NULL,
        `timestamp` BIGINT NOT NULL,
        PRIMARY KEY (`hash`),
        CONSTRAINT `Transactions_fk0` FOREIGN KEY (`member_id`) REFERENCES `DiscordMembers`(`id`)
    );
    """

create_table_payments = """
    CREATE TABLE IF NOT EXISTS `Payments` (
        `mint_id` INT NOT NULL,
        `member_id` BIGINT NOT NULL,
        `amount_of_checkouts` INT NOT NULL DEFAULT '0',
        PRIMARY KEY (`mint_id`, `member_id`),
        CONSTRAINT `Payments_fk0` FOREIGN KEY (`mint_id`) REFERENCES `Mints`(`id`),
        CONSTRAINT `Payments_fk1` FOREIGN KEY (`member_id`) REFERENCES `DiscordMembers`(`id`)
);"""

drop_table = "DROP TABLE {table_name}"

delete_all_data_from_table = "DELETE FROM {table_name}"

add_data = "INSERT INTO {table_and_columns} values ({values})"

change_data = "UPDATE {table} SET {data_to_change} WHERE {primary_key}"

delete_data = "DELETE FROM {table} WHERE {primary_key}"

select_data = "SELECT {data_to_select} FROM {table} WHERE {condition}"

select_data_with_joins = "SELECT {data_to_select} FROM {table} {joins} WHERE {condition}"
