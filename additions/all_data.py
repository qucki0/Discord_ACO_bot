from solana.rpc.api import Client

from classes.classes import Config
from classes.sql_client import SqlClient

config = Config.parse_file("config.json")
sql_client = SqlClient(config.sql_data.user, config.sql_data.password, config.sql_data.db_name, config.sql_data.host,
                       config.sql_data.port)
sql_client.start()
solana_client = Client(config.rpc_link)
