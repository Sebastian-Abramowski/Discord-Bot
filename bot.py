import discord
from discord.ext import commands
from discord import app_commands
import responses


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    token = None
    with open("token.txt", 'r') as file_handle:
        token = file_handle.read()

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f"{bot.user} is now running")

        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    @bot.tree.command(name="hello", description="Get greeted")
    async def hello(interaction: discord.Interaction):
        response = responses.handle_response("hello")
        await interaction.response.send_message(response)

    @bot.tree.command(name="getint", description="Get some number")
    async def getint(interaction: discord.Interaction):
        response = responses.handle_response("getInt")
        await interaction.response.send_message(response)

    @bot.tree.command(name="play")
    @app_commands.describe(arg="the link to the song")
    async def play(interaction: discord.Interaction, arg: str):
        msg = (f"{interaction.user.name} wants"
               f"to play {arg}")
        await interaction.response.send_message(msg)

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said '{user_message}' on channel {channel}")

    bot.run(token)
