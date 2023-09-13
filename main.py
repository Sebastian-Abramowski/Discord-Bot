import dotenv
import os
import music_bot


if __name__ == '__main__':
    dotenv.load_dotenv()
    music_bot.bot.run(os.getenv('DONKEY_MUSIC_BOT_TOKEN'))
