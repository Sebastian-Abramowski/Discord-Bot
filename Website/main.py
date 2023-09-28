import flask

app = flask.Flask(__name__)

music_bot_info = {
    'name': "DonkeyMusicBot",
    'title': "Tired of discord music bots that are not working?",
    'description': ("DonkeyMusicBot is a bot that lets you play and manage music. It is easy "
                    "to easy, since it makes use of slash commands in discord. Give it a try!"),
    'discord_url': ("https://discord.com/api/oauth2/authorize?client_id="
                    "1151572540075032586&permissions=35461400849472&scope=bot%20applications.commands"),
}

secondary_bot_info = {
    'name': "DonkeySecondaryBot",
    'title': "Use information from various APIs and have fun",
    'description': ("DonkeySecondaryBot is a bot that makes use of various APIs and have some random"
                    "commands. It is easy to easy, since it makes use of slash commands in discord. "
                    "Give it a try!"),
    'discord_url': ("https://discord.com/api/oauth2/authorize?client_id=1151580275478896670&permissions="
                    "277092756544&scope=bot%20applications.commands"),
}


@app.route("/")
@app.route("/home")
def home():
    return flask.render_template("home.html", title="DonkeyBots")


@app.route("/music_bot")
def music_bot():
    return flask.render_template("music_bot.html", **music_bot_info)


@app.route("/secondary_bot")
def secondary_bot():
    return flask.render_template("secondary_bot.html", **secondary_bot_info)


if __name__ == "__main__":
    app.run(debug=True)

# TODO: sprawdź zmianę na Flaska
# TODO: ze słownika arguemnty do stron botów
# TODO: ogarnij strony z komendami
# TODO: ogarnij bardziej Flaska
# TODO: add alts to imgs
