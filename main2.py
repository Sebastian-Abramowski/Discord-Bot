import os
import dotenv

from secondary_bot.secondary_bot import bot


if __name__ == '__main__':
    dotenv.load_dotenv()
    bot.run(os.getenv("DONKEY_SECONDARY_BOT_TOKEN"))
