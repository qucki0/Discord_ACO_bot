from base_classes.config import Config
from blockchains.solana.client import SolanaClient
from sql.client import SqlClient

config = Config.parse_file("config.json")
sql_client = SqlClient(user=config.sql_data.user,
                       password=config.sql_data.password,
                       db_name=config.sql_data.db_name,
                       host=config.sql_data.host,
                       port=config.sql_data.port)
sql_client.start()
solana_client = SolanaClient(config.rpc_link)
