import discord
import random
import requests
import dotenv
import os
import time
import hashlib
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
            embed = discord.Embed(color=discord.Color.orange())
            embed.add_field(name="", value=joke)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("`There was a problem with getting a random joke`")

    def get_random_joke(self) -> Union[str, None]:
        url_to_repo = os.getenv("URL_TO_MY_REPO")
        headers = {
            "User-Agent": f"My DiscordBot ({url_to_repo})",
            "Accept": "application/json",
        }
        try:
            response = requests.get("https://icanhazdadjoke.com/", headers=headers, timeout=3)
        except Exception as e:
            print("[FECTHING-RANDOM-JOKE-ERROR] " + str(e))
            return None

        if response.status_code != 200:
            return None
        return response.json()['joke']

    async def random_fact(self, interaction: discord.Interaction) -> None:
        fact = self.get_random_fact()
        if fact:
            embed = discord.Embed(color=discord.Color.purple())
            embed.add_field(name="", value=fact)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("`There was a problem with getting a random fact`")

    def get_random_fact(self) -> Union[str, None]:
        headers, payload = self.get_headers_and_params_for_api_ninjas()
        try:
            response = requests.get("https://api.api-ninjas.com/v1/facts", params=payload,
                                    headers=headers, timeout=3)
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
        embed_with_riddle = self.get_embed_with_random_riddle()
        if embed_with_riddle:
            await interaction.response.send_message(embed=embed_with_riddle)
        else:
            await interaction.response.send_message("`There was a problem with getting a random riddle`")

    def get_embed_with_random_riddle(self) -> Union[discord.Embed, None]:
        riddle_dict = self.get_dict_with_random_riddle()

        if not riddle_dict:
            return None

        title = riddle_dict["title"]
        question = riddle_dict["question"]
        answer = riddle_dict["answer"]

        embed = discord.Embed(color=discord.Color.pink(), title=title, description=question)
        embed.add_field(name="See answer: ", value=f"||{answer}||")
        return embed

    def get_dict_with_random_riddle(self) -> Union[dict[str, str], None]:
        headers, payload = self.get_headers_and_params_for_api_ninjas()
        try:
            response = requests.get("https://api.api-ninjas.com/v1/riddles", params=payload,
                                    headers=headers, timeout=3)
        except Exception as e:
            print("[FECTHING-RANDOM-RIDDLE-ERROR] " + str(e))
            return None
        if response.status_code != 200:
            return None
        riddle = response.json()[0]

        return riddle

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
                                    headers=headers, timeout=3)
        except Exception as e:
            print("[FECTHING-RANDOM-CAT-IMAGE-ERROR] " + str(e))
            return None
        if response.status_code != 200:
            return None
        return response.json()[0]["url"]


class MarvelCharacter():
    def __init__(self):
        self.name = None
        self.description = None
        self.image_url = None
        self.num_of_comics = None
        self.num_of_matching_characters = None  # either 0 or 1 (limit=1)
        self.partly_maching_names = None

    def __str__(self):
        list_of_attributes = [self.name, self.description, self.image_url,
                              self.num_of_comics, self.num_of_matching_characters,
                              self.partly_maching_names]
        return "\n".join([str(attr) for attr in list_of_attributes])


class DonkeySecondaryBot(RandomBot):
    def __init__(self):
        super().__init__()

    async def check_movie(self, interaction: discord.Interaction, title: str) -> None:
        embed = self.get_movie_embed_info_by_title(title)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"`There was a problem with getting the info of the movie called` **{title}**")

    def get_movie_embed_info_by_title(self, title: str) -> Union[discord.Embed, None]:
        movie_info_dict = self.get_movie_info_by_title(title)

        if not movie_info_dict:
            return None

        movie_title = movie_info_dict["Title"]
        year = movie_info_dict["Year"]
        released_date = movie_info_dict["Released"]
        plot_summary = movie_info_dict["Plot"]
        poster_image_url = movie_info_dict["Poster"]
        runtime = movie_info_dict["Runtime"]
        actors = movie_info_dict["Actors"]
        imdb_rating = movie_info_dict["imdbRating"]

        embed = discord.Embed(color=discord.Color.blue(), title=movie_title)
        embed.set_image(url=poster_image_url)
        embed.add_field(name="Plot", value=plot_summary, inline=False)
        embed.add_field(name="Year", value=year)
        embed.add_field(name="Released date", value=released_date)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="Runtime", value=runtime)
        embed.add_field(name="IMDB rating", value=f"{imdb_rating}/10")
        embed.add_field(name="Actors", value=actors, inline=False)

        return embed

    def get_movie_info_by_title(self, title: str) -> Union[dict[str, str], None]:
        # Returns movie info and url to the image of the poster or None, None
        omdbapi_api_key = os.getenv("OMDB_API_API_KEY")
        params = {
            "t": title
        }
        try:
            response = requests.get(f"http://www.omdbapi.com/?apikey={omdbapi_api_key}&",
                                    params=params)
        except Exception as e:
            print("[FECTHING-MOVIE-ERROR] " + str(e))
            return None
        response = response.json()

        if response["Response"] == "False":
            return None

        return response

    async def check_marvel_character(self, interaction: discord.Interaction, name: str) -> None:
        marvel_character = self.get_marvel_character(name)
        if not marvel_character:
            await interaction.response.send_message(
                f"`There was a problem with fetching information about {name}`")
            return None

        if marvel_character.num_of_matching_characters == 0:
            if marvel_character.partly_maching_names:
                names = ", ".join(marvel_character.partly_maching_names)
                msg = ("You need to be more specific. These are "
                       f"similar names of characters in our data: {names}")
                await interaction.response.send_message(msg)
                return None
            else:
                await interaction.response.send_message(
                    f"No marvel character with name of: '{name}' found")
                return None

        try:
            embed = discord.Embed(color=discord.Color.red(), title=marvel_character.name)
            embed.set_image(url=marvel_character.image_url)
            embed.add_field(name="Description", value=marvel_character.description, inline=False)
            embed.add_field(name="Appeared/mentioned in:", value=f"{marvel_character.num_of_comics} comics")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"There was a problem with showing infrormation about {name}")

    def get_marvel_character(self, name: str) -> Union[MarvelCharacter, None]:
        marvel_api_public_key = os.getenv("MARVEL_API_PUBLIC_KEY")
        marvel_api_private_key = os.getenv("MARVEL_API_PRIVATE_KEY")
        ts = str(time.time())
        hash_input = ts + marvel_api_private_key + marvel_api_public_key
        # Get hexadecimal representation of hashed, in md5 algorithm, value
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()

        params = {
            "name": name,
            "ts": ts,
            "apikey": marvel_api_public_key,
            "hash": hash_value,
            "limit": 1,
        }

        try:
            response = requests.get("http://gateway.marvel.com/v1/public/characters",
                                    params=params, timeout=3)
        except Exception as e:
            print(e)
            return None
        response = response.json()

        if response['code'] != 200:
            return None

        character = MarvelCharacter()

        number_of_results = response["data"]["total"]  # 0 or 1
        character.num_of_matching_characters = 0
        if number_of_results == 0:
            params = {
                "nameStartsWith": name,
                "ts": ts,
                "apikey": marvel_api_public_key,
                "hash": hash_value,
            }

            try:
                response = requests.get("http://gateway.marvel.com/v1/public/characters",
                                        params=params, timeout=3)
            except Exception as e:
                print(e)
                return None
            response = response.json()

            if response['code'] != 200:
                return None

            results = response["data"]["results"]
            names = []
            for result_dict in results:
                names.append(result_dict["name"])
            character.partly_maching_names = names
            return character

        character.num_of_matching_characters = 1

        result = response["data"]["results"][0]
        char_name = result["name"]
        description = result["description"]
        image = ".".join([result["thumbnail"]["path"], result["thumbnail"]["extension"]])
        num_of_comics = result["comics"]["available"]

        character.name = char_name
        character.description = description
        character.image_url = image
        character.num_of_comics = num_of_comics
        return character

    # TODO: check_eng_word https://www.wordsapi.com/ trzeba inny bo potrzebna karta
    # TODO: weather where https://openweathermap.org/weathermap?basemap=map&cities=true&layer=temperature&lat=52.7438&lon=20.9578&zoom=10 # noqa: E501
    # TODO: check_marvel_character
    # TODO: check_marvel_film # https://developer.marvel.com/docs

# TODO: hosting
# TODO: sprawdź type hinty
# TODO: testy drugiego bota
# TODO: README zaktualizuj environmental variables

# TODO: dokończ get_marvel_character_info + refactor


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


@bot.tree.command(name="check_movie", description="Check movie/series info by title")
@discord.app_commands.describe(title="Title of the movie/series")
async def check_movie_command(interaction: discord.Interaction, title: str):
    await bot.check_movie(interaction, title)


@bot.tree.command(name="check_marvel_character", description="Check marvel character by its name")
@discord.app_commands.describe(name="Name of character")
async def check_marvel_character_command(interaction: discord.Interaction, name: str):
    await bot.check_marvel_character(interaction, name)
