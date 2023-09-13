import discord
from basic_bot import BasicBot


class RandomBot(BasicBot):
    def __init__(self):
        super().__init__()

    async def test_random(self, interaction: discord.Interaction) -> None:
        print(self.voice_clients)
        await interaction.response.send_message("TESTING RANDOM CLASS")

    # TODO: flip_coin
    # TODO: random_joke
    # TODO: random_num num1 num2
    # TODO: random_fact
    # TODO: random_shrek


class DonkeySecondaryBot(RandomBot):
    def __init__(self):
        super().__init__()

    # TODO: check_eng_word
    # TODO: weather where
    # TODO: check_movie movie
    # TODO: check_marvel_character
    # TODO: check_marvel_film # https://developer.marvel.com/docs


# TODO: hosting
# TODO: sprawdź type hinty
# TODO: poczytaj o API
# TODO: podział na dwa różne boty
# TODO: testy MusicBota
# TODO: testy drugiego bota
# TODO: wyłączenie self.if_looped w trakcie grania i próba puszczenia przez /play


bot = DonkeySecondaryBot()


@bot.tree.command(name="test_random", description="TESTING")
async def test_random_command(interaction: discord.Interaction):
    await bot.test_random(interaction)
