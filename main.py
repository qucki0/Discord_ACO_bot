import config
from discord_client import DiscordClient

client = DiscordClient(config.PREFIX)
client.run(config.TOKEN)
