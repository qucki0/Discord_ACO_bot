from base_classes.config import ConfigClass


async def start_sql_client() -> None:
    from sql.client import SqlClient
    sql_client = SqlClient(user=config.sql_data.user,
                           password=config.sql_data.password,
                           db_name=config.sql_data.db_name,
                           host=config.sql_data.host,
                           port=config.sql_data.port)
    await sql_client.start()


config = ConfigClass.parse_file("config.json")
