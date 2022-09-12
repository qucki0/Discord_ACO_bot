from discord_client import *

client = DiscordClient(config.PREFIX)
client.tree.add_command(Mints())
client.tree.add_command(Aco())
client.run(config.TOKEN)
