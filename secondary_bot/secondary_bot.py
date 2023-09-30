import os
import random
import requests
import time
import hashlib
from typing import Union, Tuple, NamedTuple, Optional

import discord
import dotenv

from secondary_bot.marvel_character import MarvelCharacter
from bot.basic_bot import BasicBot
import utilities.format

dotenv.load_dotenv()


class RandomBot(BasicBot):
    def __init__(self, name: str):
        super().__init__(name)

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

    def get_random_joke(self) -> Optional[str]:
        try:
            url_to_repo = os.getenv("URL_TO_MY_REPO")
            headers = {
                "User-Agent": f"My DiscordBot ({url_to_repo})",
                "Accept": "application/json",
            }
            response = requests.get("https://icanhazdadjoke.com/", headers=headers, timeout=3)
            if response.status_code != 200:
                return None
            return response.json()['joke']
        except Exception as e:
            print("[FECTHING-RANDOM-JOKE-ERROR] " + str(e))
            return None

    async def random_fact(self, interaction: discord.Interaction) -> None:
        fact = self.get_random_fact()
        if fact:
            embed = discord.Embed(color=discord.Color.purple())
            embed.add_field(name="", value=fact)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("`There was a problem with getting a random fact`")

    def get_random_fact(self) -> Optional[str]:
        try:
            headers, payload = self.get_headers_and_params_for_api_ninjas()
            response = requests.get("https://api.api-ninjas.com/v1/facts", params=payload,
                                    headers=headers, timeout=3)
            if response.status_code != 200:
                return None
            return response.json()[0]['fact']
        except Exception as e:
            print("[FECTHING-RANDOM-FACT-ERROR] " + str(e))
            return None

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

    def get_embed_with_random_riddle(self) -> Optional[discord.Embed]:
        riddle_dict = self.get_dict_with_random_riddle()

        if not riddle_dict:
            return None

        title = riddle_dict["title"]
        question = riddle_dict["question"]
        answer = riddle_dict["answer"]

        embed = discord.Embed(color=discord.Color.pink(), title=title, description=question)
        embed.add_field(name="See answer: ", value=f"||{answer}||")
        return embed

    def get_dict_with_random_riddle(self) -> Optional[dict[str, str]]:
        try:
            headers, payload = self.get_headers_and_params_for_api_ninjas()
            response = requests.get("https://api.api-ninjas.com/v1/riddles", params=payload,
                                    headers=headers, timeout=3)
            if response.status_code != 200:
                return None
            riddle = response.json()[0]
            return riddle
        except Exception as e:
            print("[FECTHING-RANDOM-RIDDLE-ERROR] " + str(e))
            return None

    async def random_cat_image(self, interaction: discord.Interaction) -> None:
        cat_img_url = self.get_random_cat_image()
        if cat_img_url:
            await interaction.response.send_message(cat_img_url)
        else:
            await interaction.response.send_message(
                "`There was a problem with getting a random cat image`")

    def get_random_cat_image(self) -> Optional[str]:
        # It returns url to an image (str) or None
        try:
            thecatapi_api_key = os.getenv("THECATAPI_API_KEY")
            headers = {
                "x-api-key": thecatapi_api_key,
            }
            response = requests.get("https://api.thecatapi.com/v1/images/search?limit=1",
                                    headers=headers, timeout=3)
            if response.status_code != 200:
                return None
            return response.json()[0]["url"]
        except Exception as e:
            print("[FECTHING-RANDOM-CAT-IMAGE-ERROR] " + str(e))
            return None


class SecondaryBot(RandomBot):
    def __init__(self, name: str):
        super().__init__(name)

    async def on_ready(self) -> None:
        await super().on_ready()
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(
                                       type=discord.ActivityType.watching, name="/command"))

    async def check_movie(self, interaction: discord.Interaction, title: str) -> None:
        embed = self.get_movie_embed_info_by_title(title)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"`There was a problem with getting the info of the movie called` **{title}**")

    def get_movie_embed_info_by_title(self, title: str) -> Optional[discord.Embed]:
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
        try:
            omdbapi_api_key = os.getenv("OMDB_API_API_KEY")
            params = {
                "t": title
            }
            response = requests.get(f"http://www.omdbapi.com/?apikey={omdbapi_api_key}&",
                                    params=params)
            response = response.json()
            if response["Response"] == "False":
                return None
            return response
        except Exception as e:
            print("[FECTHING-MOVIE-ERROR] " + str(e))
            return None

    async def check_marvel_character(self, interaction: discord.Interaction, name: str) -> None:
        marvel_character = self.get_marvel_character(name)
        if not marvel_character:
            await self.respond_or_followup(
                interaction,
                f"`There was a problem with fetching information about {name}`")
            return None

        if marvel_character.num_of_matching_characters == 0:
            await self.respond_if_no_matching_marvel_character_found(interaction, marvel_character,
                                                                     passed_character_name=name)
        else:
            await self.respond_if_matching_marvel_character_found(interaction, marvel_character,
                                                                  passed_character_name=name)

    async def respond_or_followup(self, interaction: discord.Interaction, message: str,
                                  embed: discord.Embed = None) -> None:
        try:
            if not interaction.is_expired():
                await interaction.response.send_message(message, embed=embed)
        except discord.errors.InteractionResponded:
            if not interaction.is_expired():
                await interaction.followup.send(message, embed=embed)
        except Exception as e:
            print("[ERROR] " + str(e))

    def get_marvel_character(self, name: str) -> Optional[MarvelCharacter]:
        try:
            marvel_character = self._get_marvel_character(name)
            return marvel_character
        except Exception as e:
            print("[ERROR] " + str(e))
            return None

    def _get_marvel_character(self, name: str) -> Optional[MarvelCharacter]:
        response = self.get_response_from_marvel_characters_api_by_name(name)
        if not self.is_marvel_api_response_valid(response):
            return None

        character = MarvelCharacter()

        number_of_results = response["data"]["total"]  # 0 or 1 (limit=1)
        character.num_of_matching_characters = 0
        if number_of_results == 0:
            response = self.get_response_from_marvel_characters_api_by_name_beginning(
                name_beginning=name)
            if not self.is_marvel_api_response_valid(response):
                return None
            results = response["data"]["results"]
            if_character_updated = character.update_partly_matching_names(results)
        else:
            character.num_of_matching_characters = 1
            result = response["data"]["results"][0]
            if_character_updated = character.update_with_found_result(result)

        if not if_character_updated:
            return None
        return character

    def is_marvel_api_response_valid(self, response: Optional[dict[str, object]]) -> bool:
        if not response:
            return False
        if response.get('code', 0) != 200:
            return False
        return True

    def get_response_from_marvel_characters_api_by_name(self, name: str) -> Optional[dict[str, object]]:
        try:
            marvel_api_info = self.get_marvel_api_info()
            params = {
                "name": name,
                "ts": marvel_api_info.ts,
                "apikey": marvel_api_info.apikey,
                "hash": marvel_api_info.hash,
                "limit": 1,
            }

            response = requests.get("http://gateway.marvel.com/v1/public/characters",
                                    params=params, timeout=3)
            response = response.json()
            return response
        except Exception as e:
            print("[ERROR] " + str(e))
            return None

    def get_marvel_api_info(self) -> NamedTuple:
        marvel_api_public_key = os.getenv("MARVEL_API_PUBLIC_KEY")
        marvel_api_private_key = os.getenv("MARVEL_API_PRIVATE_KEY")
        ts = str(time.time())
        hash_input = ts + marvel_api_private_key + marvel_api_public_key
        # Get hexadecimal representation of hashed, in md5 algorithm, value
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()

        class MarvelApiInfo(NamedTuple):
            ts: str
            apikey: str
            hash: str

        return MarvelApiInfo(ts, marvel_api_public_key, hash_value)

    def get_response_from_marvel_characters_api_by_name_beginning(self, name_beginning: str
                                                                  ) -> Union[dict[str, object], None]:
        try:
            marvel_api_info = self.get_marvel_api_info()
            params = {
                    "nameStartsWith": name_beginning,
                    "ts": marvel_api_info.ts,
                    "apikey": marvel_api_info.apikey,
                    "hash": marvel_api_info.hash,
                }

            response = requests.get("http://gateway.marvel.com/v1/public/characters",
                                    params=params, timeout=3)
            response = response.json()
            return response
        except Exception as e:
            print("[ERROR] " + str(e))
            return None

    async def respond_if_no_matching_marvel_character_found(self, interaction: discord.Interaction,
                                                            marvel_character: MarvelCharacter,
                                                            passed_character_name: str) -> None:
        if marvel_character.partly_maching_names:
            if len(marvel_character.partly_maching_names) == 1:
                await interaction.response.defer(thinking=True)
                proper_name = marvel_character.partly_maching_names[0]
                await self.check_marvel_character(interaction, proper_name)
                return None
            names = ", ".join(marvel_character.partly_maching_names)
            msg = ("You need to be more specific. These are "
                   f"similar names of characters in our data: {names}")
            await self.respond_or_followup(interaction, msg)
            return None
        else:
            await self.respond_or_followup(
                interaction,
                f"No marvel character with name of: '{passed_character_name}' found")
            return None

    async def respond_if_matching_marvel_character_found(self, interaction: discord.Interaction,
                                                         marvel_character: MarvelCharacter,
                                                         passed_character_name: str) -> None:
        try:
            embed = discord.Embed(color=discord.Color.red(), title=marvel_character.name)
            embed.set_image(url=marvel_character.image_url)
            embed.add_field(name="Description", value=marvel_character.description, inline=False)
            embed.add_field(name="Appeared/mentioned in:",
                            value=f"{marvel_character.num_of_comics} comics")
            await self.respond_or_followup(interaction, message=None, embed=embed)
        except Exception as e:
            print("[ERROR] " + str(e))
            await self.respond_or_followup(
                interaction,
                f"There was a problem with showing infrormation about {passed_character_name}")

    async def check_country(self, interaction: discord.Interaction, name: str) -> None:
        embed = self.get_country_embed_info_by_name(name)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"`No information about the country called` **{name}** `found`")

    def get_country_embed_info_by_name(self, name: str) -> Optional[discord.Embed]:
        try:
            country_info = self.get_info_about_country_by_name(name)
            country_name = country_info["name"]
            capital = country_info["capital"]
            region = country_info["region"]
            population = utilities.format.format_wide_number(country_info["population"], " ")
            timezone = ", ".join(list(country_info["timezones"]))
            languages = ", ".join(list(country_info["languages"].values()))
            flag = country_info["flag"]["large"]
            currencies = ", ".join(
                [currency["name"] for currency in country_info["currencies"].values()])

            embed = discord.Embed(color=discord.Color.yellow(), title=country_name)
            embed.set_image(url=flag)
            embed.add_field(name="Capital: ", value=capital)
            embed.add_field(name="Region: ", value=region)
            embed.add_field(name="Population: ", value=population)
            embed.add_field(name="Timezone: ", value=timezone)
            embed.add_field(name="Languages: ", value=languages)
            embed.add_field(name="Currencies: ", value=currencies)
            return embed
        except Exception as e:
            print("[ERROR] " + str(e))
            return None

    def get_info_about_country_by_name(self, name: str) -> Optional[dict[str, object]]:
        try:
            name = "United States" if name.lower() in ["usa", "us", "united states of america"] else name

            apikey = os.getenv("COUNTRYAPI_API_KEY")
            params = {
                "apikey": apikey
            }
            url = f"https://countryapi.io/api/name/{name}"

            response = requests.get(url, params=params)
            if 'error' in response or response.status_code != 200:
                return None

            country_dict_info = list(response.json().values())[0]
            return country_dict_info
        except Exception as e:
            print("[ERROR] " + str(e))
            return None


bot = SecondaryBot(name="DonkeySecondaryBot")


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


@bot.tree.command(name="check_country", description="Check country info by its name")
@discord.app_commands.describe(name="Name of country")
async def check_country_command(interaction: discord.Interaction, name: str):
    await bot.check_country(interaction, name)
