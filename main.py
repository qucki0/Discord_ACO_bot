import config
from discord_client import *

client = DiscordClient(config.PREFIX)
client.tree.add_command(Mints())
client.run(config.TOKEN)

