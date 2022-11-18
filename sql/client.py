import asyncio

import aiomysql
import aiomysql.cursors

from base_classes.base import SingletonBase
from sql import queries
from utilities.logging import get_logger
from utilities.strings import get_sql_str_from_dict

logger = get_logger(__name__)


class SqlBase(SingletonBase):
    ready = False

    def __init__(self, user: str = "root", password: str = "pass", db_name: str = "TEST_DB", host: str = '127.0.0.1',
                 port: int = 3306):
        if not self.ready:
            self.user = user
            self.password = password
            self.db_name = db_name
            self.host = host
            self.port = port
            self.pool: aiomysql.Pool | None = None

    async def connect(self) -> None:
        logger.debug(f"Connecting to database {self.host}::{self.port}")
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db_name,
            cursorclass=aiomysql.cursors.DictCursor,
            autocommit=True,
            loop=asyncio.get_running_loop(),
            minsize=0,
            maxsize=25,
            pool_recycle=60 * 5
        )

    async def start(self) -> None:
        await self.connect()
        self.ready = True

    async def stop(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()
        self.ready = False

    async def execute_query(self, query) -> list[dict[str: int | str]]:
        logger.debug(f"Executing query: {query}")
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query)
                data = await cursor.fetchall()
        logger.debug(f"Response: {data}")
        return data

    async def execute_queries(self, queries_list: list[str]) -> None:
        tasks = [asyncio.create_task(self.execute_query(query)) for query in queries_list]
        await asyncio.gather(*tasks)


class SqlClient(SqlBase):

    async def create_tables(self) -> None:
        setup_tables = [queries.create_table_discord_members, queries.create_table_mints,
                        queries.create_table_payments, queries.create_table_wallets,
                        queries.create_table_transactions]
        for q in setup_tables:
            await self.execute_query(q)

    async def drop_tables(self) -> None:
        tables = ["Transactions", "Wallets", "Payments", "Mints", "DiscordMembers"]
        for table in tables:
            await self.execute_query(queries.drop_table.format(table_name=table))

    async def delete_all_data(self) -> None:
        tables = ["Transactions", "Wallets", "Payments", "Mints", "DiscordMembers"]
        delete_queries = [queries.delete_all_data_from_table.format(table_name=table) for table in tables]
        await self.execute_queries(delete_queries)

    async def add_data(self, table: str, data_to_add: dict[str: int | str]):
        keys_as_str = ", ".join([key for key in data_to_add])
        columns_to_add = f"{table}({keys_as_str})"
        values_to_add = []
        for key in data_to_add:
            value = data_to_add[key]
            match value:
                case str():
                    values_to_add.append(f"'{value}'")
                case int() | float():
                    values_to_add.append(f"{value}")
                case None:
                    values_to_add.append("NULL")
        query = queries.add_data.format(table_and_columns=columns_to_add, values=", ".join(values_to_add))
        await self.execute_query(query)

    async def change_data(self, table: str, data_to_change: dict[str: int | str],
                          primary_key: dict[str: int | str]) -> None:
        data_to_change_str = get_sql_str_from_dict(data_to_change, ", ", False)
        primary_key_str = get_sql_str_from_dict(primary_key, " and ", False)
        query = queries.change_data.format(table=table, data_to_change=data_to_change_str,
                                           primary_key=primary_key_str)
        await self.execute_query(query)

    async def delete_data(self, table: str, primary_key: dict[str: int | str]) -> None:
        primary_key_str = get_sql_str_from_dict(primary_key, " and ", False)
        query = queries.delete_data.format(table=table, primary_key=primary_key_str)
        await self.execute_query(query)

    async def select_data(self, table: str, data_to_select: list[str] = None, condition: dict[str: int | str] = None,
                          join_tables: list[str] = None, join_conditions: list[str] = None) \
            -> list[dict[str: int | str]]:
        if data_to_select is not None:
            data_to_select_str = ", ".join(data_to_select)
        else:
            data_to_select_str = "*"

        if condition is not None:
            condition_str = get_sql_str_from_dict(condition, " AND ", True)
        else:
            condition_str = "1"

        if join_tables is not None:
            joins = []
            for join_table, join_condition in zip(join_tables, join_conditions):
                joins.append(f"JOIN {join_table} ON {join_condition}")
            joins_str = " ".join(joins)
            query = queries.select_data_with_joins.format(data_to_select=data_to_select_str, joins=joins_str,
                                                          table=table, condition=condition_str)
        else:
            query = queries.select_data.format(data_to_select=data_to_select_str, table=table, condition=condition_str)
        data = await self.execute_query(query)
        return data
