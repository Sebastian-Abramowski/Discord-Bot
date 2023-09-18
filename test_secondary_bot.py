from secondary_bot import DonkeySecondaryBot

bot = DonkeySecondaryBot(name="Jo")
# Testing if API calls return something


def test_get_random_joke():
    assert bot.get_random_joke()
    assert len(bot.get_random_joke().split()) > 2


def test_get_random_fact():
    assert bot.get_random_fact()
    assert len(bot.get_random_fact().split()) > 2


def test_get_dict_with_random_riddle():
    assert bot.get_dict_with_random_riddle()


def test_get_random_cat_image():
    assert bot.get_random_cat_image()


def test_get_movie_info_by_title_non_existent():
    assert not bot.get_movie_info_by_title("some weird name of the movie")
    assert not bot.get_movie_info_by_title("The rise of Donkey")


def test_get_movie_info_by_title_existent1():
    assert bot.get_movie_info_by_title("Oppenheimer")
    assert bot.get_movie_info_by_title("Puss in boots: the last wish")
    assert bot.get_movie_info_by_title("Shrek")


def test_get_movie_info_by_title_existent2():
    assert bot.get_movie_info_by_title("Se7en")
    assert bot.get_movie_info_by_title("Fight club")
    assert bot.get_movie_info_by_title("fIGhT ClUb")


def test_get_marvel_character_a_few_possible_matches():
    spider_man = bot.get_marvel_character("Spider-man")
    assert not spider_man.name
    assert spider_man.num_of_matching_characters == 0
    assert len(spider_man.partly_maching_names) > 1


def test_get_marvel_character_one_exact_match():
    hulk = bot.get_marvel_character("Hulk")
    assert hulk.name
    assert hulk.image_url
    assert hulk.description
    assert hulk.num_of_comics
    assert hulk.num_of_matching_characters == 1
    assert not hulk.partly_maching_names


def test_get_marvel_character_one_inexact_match():
    baron = bot.get_marvel_character("Baron mordo")
    assert len(baron.partly_maching_names) == 1
    assert baron.num_of_matching_characters == 0

    baron = bot.get_marvel_character("Baron Mordo (Karl Mordo)")
    assert baron.name == "Baron Mordo (Karl Mordo)"
    assert baron.num_of_matching_characters == 1
    assert not baron.partly_maching_names


def test_get_marvel_character_non_existent1():
    not_groot = bot.get_marvel_character("Groot the Great")
    assert not_groot.num_of_matching_characters == 0
    assert not not_groot.partly_maching_names
    assert not not_groot.name


def test_get_marvel_character_non_existent2():
    donkey = bot.get_marvel_character("Donkey")
    assert donkey.num_of_matching_characters == 0
    assert not donkey.partly_maching_names
    assert not donkey.name


def test_get_info_about_country_by_name_existent1():
    assert bot.get_info_about_country_by_name("Poland")
    assert bot.get_info_about_country_by_name("Moldova")
    assert bot.get_info_about_country_by_name("Spain")


def test_get_info_about_country_by_name_existent2():
    assert bot.get_info_about_country_by_name("iTaLy")
    assert bot.get_info_about_country_by_name("itALY")
    assert bot.get_info_about_country_by_name("italy")


def test_get_info_about_country_by_name_existent3():
    assert bot.get_info_about_country_by_name("Germany")
    assert bot.get_info_about_country_by_name("Albania")
    assert bot.get_info_about_country_by_name("france")


def test_get_info_about_country_by_name_usa():
    assert bot.get_info_about_country_by_name("United States of America")
    assert bot.get_info_about_country_by_name("United States")
    assert bot.get_info_about_country_by_name("usa")
    assert bot.get_info_about_country_by_name("US")


def test_get_info_about_country_by_name_non_existent():
    assert not bot.get_info_about_country_by_name("Moldavia")
    assert not bot.get_info_about_country_by_name("Rapture")
    assert not bot.get_info_about_country_by_name("Kyrat")
    assert not bot.get_info_about_country_by_name("Toussaint")
