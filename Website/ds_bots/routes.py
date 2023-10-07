from flask import render_template

from ds_bots.models import Command
from ds_bots import app


music_bot_info = {
    'name': "DonkeyMusicBot",
    'title': "Tired of discord music bots that are not working?",
    'description': ("DonkeyMusicBot is a bot that lets you play and manage music. It is easy "
                    "to easy, since it makes use of slash commands in discord. Give it a try!"),
    'commands_route': "/music_bot/commands",
    'discord_url': ("https://discord.com/api/oauth2/authorize?client_id="
                    "1151572540075032586&permissions=35461400849472&scope=bot%20applications.commands"),
}

secondary_bot_info = {
    'name': "DonkeySecondaryBot",
    'title': "Use information from various APIs and have fun",
    'description': ("DonkeySecondaryBot is a bot that makes use of various APIs and have some random"
                    "commands. It is easy to easy, since it makes use of slash commands in discord. "
                    "Give it a try!"),
    'commands_route': '/secondary_bot/commands',
    'discord_url': ("https://discord.com/api/oauth2/authorize?client_id=1151580275478896670&permissions="
                    "277092756544&scope=bot%20applications.commands"),
}


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="DonkeyBots")


@app.route("/music_bot")
def music_bot():
    return render_template("music_bot.html", **music_bot_info)


@app.route("/music_bot/commands")
def music_bot_commands():
    return render_template("music_bot_commands.html", title="DonkeyMusicBot commands",
                           commands=Command.query.filter_by(bot_name="DonkeyMusicBot").order_by(
                               Command.category.desc()).all(),
                           categories=Command.query.filter_by(bot_name="DonkeyMusicBot").with_entities(
                               Command.category).distinct().all())


@app.route("/music_bot/commands/<category_name>")
def music_bot_commands_by_category(category_name: str):
    return render_template("music_bot_commands.html", title="DonkeyMusicBot commands",
                           commands=Command.query.filter_by(bot_name="DonkeyMusicBot",
                                                            category=category_name).order_by(
                                                                Command.category.desc()).all(),
                           categories=Command.query.filter_by(bot_name="DonkeyMusicBot").with_entities(
                               Command.category).distinct().all(),
                           current_category=category_name)


@app.route("/secondary_bot")
def secondary_bot():
    return render_template("secondary_bot.html", **secondary_bot_info)


@app.route("/secondary_bot/commands")
def secondary_bot_commands():
    return render_template("sec_bot_commands.html", title="DonkeySecondaryBot commands",
                           commands=Command.query.filter_by(bot_name="DonkeySecondaryBot").order_by(
                               Command.category).all(),
                           categories=Command.query.filter_by(bot_name="DonkeySecondaryBot"
                                                              ).with_entities(
                                                                  Command.category).distinct().all())


@app.route("/secondary_bot/commands/<category_name>")
def secondary_bot_commands_by_category(category_name: str):
    return render_template("sec_bot_commands.html", title="DonkeySecondaryBot commands",
                           commands=Command.query.filter_by(bot_name="DonkeySecondaryBot",
                                                            category=category_name).order_by(
                                                                Command.category.desc()).all(),
                           categories=Command.query.filter_by(bot_name="DonkeySecondaryBot"
                                                              ).with_entities(
                                                                  Command.category).distinct().all(),
                           current_category=category_name)
