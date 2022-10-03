import time
import traceback

from additions.all_data import config
from classes.discord_client import DiscordClient

try:
    client = DiscordClient()
    client.run(config.token)
except Exception as ex:
    print(ex, "\n")
    print(traceback.format_exc())
    time.sleep(10)
