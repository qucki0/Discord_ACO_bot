from my_discord.client import DiscordClient
from setup import config

client = DiscordClient()
client.run(config.token)
