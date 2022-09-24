from additions.all_data import config
from discord_client import DiscordClient

client = DiscordClient()
client.run(config.token)
