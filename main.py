import os
import dotenv

from music_bot.music_bot import bot


if __name__ == '__main__':
    dotenv.load_dotenv()
    bot.run(os.getenv("DONKEY_MUSIC_BOT_TOKEN"))
