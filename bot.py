import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import responses
import dotenv
import os

dotenv.load_dotenv()
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


async def send_message(message, user_message):
    try:
        response = responses.handle_response(user_message)
        await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f"[BOT-INFO] {bot.user} is now running")

        try:
            synced = await bot.tree.sync()
            print(f"[BOT-INFO] Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"[USER-INFO] {username} said '{user_message}' on channel {channel}")

    @bot.tree.command(name="join", description="join voice channel")
    async def join(interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            voice = interaction.guild.voice_client

            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                voice = await channel.connect()
            await interaction.response.send_message("`Joined or moved to the voice channel.`")
        else:
            await interaction.response.send_message("`You are not in a voice channel.`")

    @bot.tree.command(name="hello", description="Get greeted")
    async def hello(interaction: discord.Interaction):
        response = responses.handle_response("hello")
        await interaction.response.send_message(response)

    @bot.tree.command(name="getint", description="Get some number")
    async def getint(interaction: discord.Interaction):
        response = responses.handle_response("getInt")
        await interaction.response.send_message(response)

    @bot.tree.command(name="play", description="play some sound in a channel")
    @discord.app_commands.describe(url="the link to the song")
    async def play(interaction: discord.Interaction, url: str):
        guild = interaction.guild
        # VoiceClient associated with the specified guild (there is one bot per server)
        voice = discord.utils.get(bot.voice_clients, guild=guild)

        if voice.is_playing():
            await interaction.response.send_message("Sth is already playing")
            return
        else:
            await interaction.response.send_message("Here will be url info")

            # Use youtube-dl to extract the direct audio URL
            ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio',
                                                                        'preferredcodec': 'mp3'}]}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url = info['url']  # url to audio

            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            voice.play(source)

    bot.run(os.getenv('TOKEN'))
