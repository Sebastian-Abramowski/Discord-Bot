import discord
import random
from basic_bot import BasicBot


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

        random_number = random.randint(lower_bound, upper_bound)
        await interaction.response.send_message(
            f"Random number from range <{lower_bound}, {upper_bound}> is {random_number}")

    # TODO: random_joke https://icanhazdadjoke.com/
    # TODO: random_fact https://api-ninjas.com/api/facts
    # TODO: random_cat_image https://developers.thecatapi.com/view-account/ylX4blBYT9FaoVd6OhvR?report=bOoHBz-8t   # noqa: E501


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
# TODO: poczytaj o API
# TODO: podział na dwa różne boty
# TODO: testy MusicBota
# TODO: testy drugiego bota


bot = DonkeySecondaryBot()


@bot.tree.command(name="flip_coin", description="Flip a coin and get either heads or tails")
async def flip_coin_command(interaction: discord.Interaction):
    await bot.flip_coin(interaction)
