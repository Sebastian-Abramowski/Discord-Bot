import dotenv
import os
import secondary_bot


if __name__ == '__main__':
    dotenv.load_dotenv()
    secondary_bot.bot.run(os.getenv('DONKEY_SECONDARY_BOT_TOKEN'))
