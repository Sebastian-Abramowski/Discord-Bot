import dotenv
import os
from bot import bot


if __name__ == '__main__':
    dotenv.load_dotenv()
    bot.run(os.getenv('TOKEN'))
