import os

import requests
from loguru import logger

TOKEN = os.environ.get('TOKEN', None)

headers = {"Authorization": "token {0}".format(TOKEN)}

try:
    logger.debug("Starting to download latest bot version from server.")
    content = requests.get(
        "https://raw.githubusercontent.com/hoommoos/bot/master/bot.py",
        headers=headers,
    ).content
    with open("bot.py", "w") as f:
        f.write(content.decode("utf-8"))
        logger.success("Successfully downloaded latest bot version.")
        f.close()
except requests.HTTPError:
    logger.warning("Failed to load newest bot version, will use current.")
    pass
finally:
    logger.debug("Trying to start bot...")
    os.system("python3 -m bot")
