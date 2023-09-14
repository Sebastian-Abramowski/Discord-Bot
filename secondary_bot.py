import discord
import random
import requests
import dotenv
import os
from basic_bot import BasicBot
from typing import Union, Tuple

dotenv.load_dotenv()


class RandomBot(BasicBot):
    def __init__(self):
        super().__init__()

    async def flip_coin(self, interaction: discord.Interaction) -> None:
        heads_or_tails = random.choice(["heads", "tails"])
        await interaction.response.send_message(f"The coin landed on {heads_or_tails}")

    async def random_num(self, interaction: discord.Interaction, lower_bound: int,
                         upper_bound: int) -> None:
        if lower_bound >= upper_bound:
            await interaction.response.send_message(
                f"You passed the wrong range of numbers: <{lower_bound}, {upper_bound}>")
            return None

        random_number = random.randint(lower_bound, upper_bound)
        await interaction.response.send_message(
            f"Random number from range <{lower_bound}, {upper_bound}> is {random_number}")

    async def random_joke(self, interaction: discord.Interaction) -> None:
        joke = self.get_random_joke()
        if joke:
            await interaction.response.send_message(joke)
        else:
            await interaction.response.send_message("`There was a problem with getting a random joke`")

    def get_random_joke(self) -> Union[str, None]:
        url_to_repo = os.getenv("URL_TO_MY_REPO")
        headers = {
            "User-Agent": f"My DiscordBot ({url_to_repo})",
            "Accept": "application/json",
        }
        try:
            response = requests.get("https://icanhazdadjoke.com/", headers=headers, timeout=5)
        except Exception as e:
            print("[FECTHING-RANDOM-JOKE-ERROR] " + str(e))
            return None

        if response.status_code != 200:
            return None
        return response.json()['joke']

    async def random_fact(self, interaction: discord.Interaction) -> None:
        fact = self.get_random_fact()
        if fact:
            await interaction.response.send_message(fact)
        else:
            await interaction.response.send_message("`There was a problem with getting a random fact`")

    def get_random_fact(self) -> Union[str, None]:
        headers, payload = self.get_headers_and_params_for_api_ninjas()
        try:
            response = requests.get("https://api.api-ninjas.com/v1/facts", params=payload,
                                    headers=headers, timeout=5)
        except Exception as e:
            print("[FECTHING-RANDOM-FACT-ERROR] " + str(e))
            return None
        if response.status_code != 200:
            return None
        return response.json()[0]['fact']

    def get_headers_and_params_for_api_ninjas(self) -> Tuple[dict[str, str], dict[str, int]]:
        api_ninjas_api_key = os.getenv("API_NINJAS_API_KEY")
        headers = {
            "X-Api-Key": api_ninjas_api_key,
        }
        params = {
            "limit": 1,
        }
        return headers, params

    async def random_riddle(self, interaction: discord.Interaction) -> None:
        riddle = self.get_random_riddle()
        if riddle:
            await interaction.response.send_message(riddle)
        else:
            await interaction.response.send_message("`There was a problem with getting a random riddle`")

    def get_random_riddle(self) -> Union[str, None]:
        headers, payload = self.get_headers_and_params_for_api_ninjas()
        try:
            response = requests.get("https://api.api-ninjas.com/v1/riddles", params=payload,
                                    headers=headers, timeout=5)
        except Exception as e:
            print("[FECTHING-RANDOM-RIDDLE-ERROR] " + str(e))
            return None
        if response.status_code != 200:
            return None
        riddle = response.json()[0]
        title = riddle["title"]
        question = riddle["question"]
        answer = riddle["answer"]
        riddle_to_return = f"{title}:\n{question}\nSee answer: ||{answer}||"
        return riddle_to_return

    async def random_cat_image(self, interaction: discord.Interaction) -> None:
        cat_img_url = self.get_random_cat_image()
        if cat_img_url:
            await interaction.response.send_message(cat_img_url)
        else:
            await interaction.response.send_message(
                "`There was a problem with getting a random cat image`")

    def get_random_cat_image(self) -> Union[str, None]:
        # It returns url to an image (str) or None
        thecatapi_api_key = os.getenv("THECATAPI_API_KEY")
        headers = {
            "x-api-key": thecatapi_api_key,
        }
        try:
            response = requests.get("https://api.thecatapi.com/v1/images/search?limit=1",
                                    headers=headers, timeout=5)
        except Exception as e:
            print("[FECTHING-RANDOM-CAT-IMAGE-ERROR] " + str(e))
            return None
        if response.status_code != 200:
            return None
        return response.json()[0]["url"]


class DonkeySecondaryBot(RandomBot):
    def __init__(self):
        super().__init__()

    # TODO: check_eng_word https://www.wordsapi.com/
    # TODO: weather where https://openweathermap.org/weathermap?basemap=map&cities=true&layer=temperature&lat=52.7438&lon=20.9578&zoom=10 # noqa: E501
    # TODO: check_movie movie https://www.omdbapi.com/
    # TODO: check_marvel_character
    # TODO: check_marvel_film # https://developer.marvel.com/docs

# TODO: hosting
# TODO: sprawdź type hinty
# TODO: testy drugiego bota
# TODO: README zaktualizuj environmental variables


bot = DonkeySecondaryBot()


@bot.tree.command(name="flip_coin", description="Flip a coin and get either heads or tails")
async def flip_coin_command(interaction: discord.Interaction):
    await bot.flip_coin(interaction)


@bot.tree.command(name="random_num", description="Get random number from some range")
@discord.app_commands.describe(lower_bound="the lower bound of range",
                               upper_bound="the upper bound of range")
async def random_num_command(interaction: discord.Interaction, lower_bound: int, upper_bound: int):
    await bot.random_num(interaction, lower_bound, upper_bound)


@bot.tree.command(name="random_joke", description="Get random joke")
async def random_joke_command(interaction: discord.Interaction):
    await bot.random_joke(interaction)


@bot.tree.command(name="random_fact", description="Get random fact")
async def random_fact_command(interaction: discord.Interaction):
    await bot.random_fact(interaction)


@bot.tree.command(name="random_riddle", description="Get random riddle")
async def random_riddle_command(interaction: discord.Interaction):
    await bot.random_riddle(interaction)


@bot.tree.command(name="random_cat_image", description="Get random cat image")
async def random_cat_image_command(interaction: discord.Interaction):
    await bot.random_cat_image(interaction)
