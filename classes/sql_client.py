import pymysql
import pymysql.cursors

import additions.sql_queries as queries


class SqlBase:

    def __init__(self, user: str = "root", password: str = "pass", db_name: str = "TEST_DB", host: str = '127.0.0.1',
                 port: int = 3306):
        self.user = user
        self.password = password
        self.db_name = db_name
        self.host = host
        self.port = port
        self.connection = None

    def connect(self) -> None:
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

    def stop(self) -> None:
        self.connection.close()

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def execute_query_and_commit(self, query: str) -> None:
        self.execute_query(query)
        self.commit()

    def commit(self) -> None:
        self.connection.commit()


class SqlClient(SqlBase):
    @staticmethod
    def get_dict_as_str_for_changes(data_to_change: dict[str: int | str], separator: str) -> str:
        changes = []
        for key in data_to_change:
            value = data_to_change[key]
            if isinstance(value, str):
                changes.append(f"{key} = '{value}'")
            elif isinstance(value, int | float):
                changes.append(f"{key} = {value}")
            elif value is None:
                changes.append(f"{key} = NULL")
        return separator.join(changes)

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
            if isinstance(value, str):
                values_to_add.append(f"'{value}'")
            elif isinstance(value, int | float):
                values_to_add.append(f"{value}")
            elif value is None:
                values_to_add.append("NULL")
        query = queries.add_data.format(table_and_columns=columns_to_add, values=", ".join(values_to_add))
        self.execute_query_and_commit(query)

    def change_data(self, table: str, data_to_change: dict[str: int | str], primary_key: dict[str: int | str]) -> None:
        data_to_change_str = self.get_dict_as_str_for_changes(data_to_change, ", ")
        primary_key_str = self.get_dict_as_str_for_changes(primary_key, " and ")
        query = queries.change_data.format(table=table, data_to_change=data_to_change_str,
                                           primary_key=primary_key_str)
        self.execute_query_and_commit(query)

    def delete_data(self, table: str, primary_key: dict[str: int | str]) -> None:
        primary_key_str = self.get_dict_as_str_for_changes(primary_key, " and ")
        query = queries.delete_data.format(table=table, primary_key=primary_key_str)
        self.execute_query_and_commit(query)
