from music_bot.music_bot import MusicBot
# flake8: noqa

bot = MusicBot(name="Jo")

# Only methods that don't require discord were tested below, the other ones were tested manually


def test_constructor():
    assert not bot.if_looped
    assert not bot.is_preparing_to_play
    assert not bot.if_queue_was_stopped
    assert not bot.if_skipped
    assert len(bot.url_queue.queue) == 0
    assert bot.name == "Jo"


def test_get_validated_url():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert bot.get_validated_url(url) == url
    assert bot.get_validated_url("rick roll") == url
    assert bot.get_validated_url("already good", if_play_next_in_queue=True) == "already good"


def test_get_url_from_search_query():
    assert bot.get_url_from_search_query("rick roll") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert bot.get_url_from_search_query("all star") == "https://www.youtube.com/watch?v=L_jWHffIx5E"
    assert bot.get_url_from_search_query("shrek playing saxophone") in ["https://www.youtube.com/watch?v=jKf6S5XI8Ew",
                                                                        "https://www.youtube.com/watch?v=_S7WEVLbQ-Y"]


def test_is_url_valid():
    assert not bot.is_url_valid("uga buga")[0]
    assert bot.is_url_valid("https://www.youtube.com/watch?v=jKf6S5XI8Ew")[0]
    assert not bot.is_url_valid("https://www.youtube.com/watch?v=B7xai5u_tnk&list=RDB7xai5u_tnk&start_radio=1")[0]


def test_is_url_youtube_playlist():
    assert not bot.is_url_youtube_playlist("Uga buga")
    assert not bot.is_url_youtube_playlist("https://www.youtube.com/watch?v=jKf6S5XI8Ew")
    assert bot.is_url_youtube_playlist("https://www.youtube.com/watch?v=B7xai5u_tnk&list=RDB7xai5u_tnk&start_radio=1")
