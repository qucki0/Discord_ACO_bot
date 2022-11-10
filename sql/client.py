import pymysql
import pymysql.cursors

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
            self.connection = None

    def connect(self) -> None:
        logger.debug(f"Connecting to database {self.host}::{self.port}")
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

    def start(self) -> None:
        self.connect()
        self.ready = True

    def stop(self) -> None:
        self.connection.close()

    def execute_query(self, query) -> list[dict[str: int | str]]:
        self.connection.ping(reconnect=True)
        logger.debug(f"executing query: {query}")
        cursor = self.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        logger.debug(f"Response: {data}")
        return data

    def execute_query_and_commit(self, query: str) -> None:
        self.execute_query(query)
        self.commit()

    def commit(self) -> None:
        self.connection.commit()


class SqlClient(SqlBase):

    def create_tables(self) -> None:
        setup_tables = [queries.create_table_discord_members, queries.create_table_mints,
                        queries.create_table_payments, queries.create_table_wallets,
                        queries.create_table_transactions]
        for q in setup_tables:
            self.execute_query(q)

    def add_data(self, table: str, data_to_add: dict[str: int | str]):
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
        self.execute_query_and_commit(query)

    def change_data(self, table: str, data_to_change: dict[str: int | str], primary_key: dict[str: int | str]) -> None:
        data_to_change_str = get_sql_str_from_dict(data_to_change, ", ", False)
        primary_key_str = get_sql_str_from_dict(primary_key, " and ", False)
        query = queries.change_data.format(table=table, data_to_change=data_to_change_str,
                                           primary_key=primary_key_str)
        self.execute_query_and_commit(query)

    def delete_data(self, table: str, primary_key: dict[str: int | str]) -> None:
        primary_key_str = get_sql_str_from_dict(primary_key, " and ", False)
        query = queries.delete_data.format(table=table, primary_key=primary_key_str)
        self.execute_query_and_commit(query)

    def select_data(self, table: str, data_to_select: list[str] = None, condition: dict[str: int | str] = None,
                    join_tables: list[str] = None, join_conditions: list[str] = None) -> list[dict[str: int | str]]:

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

        data = self.execute_query(query)
        return data
