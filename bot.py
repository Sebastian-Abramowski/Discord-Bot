import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


# commands.Bot is subclass of discord.Client
class DonkeyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".", intents=discord.Intents.all())
        self.if_looped = False

    async def on_ready(self):
        print(f"[BOT-INFO] {self.user} is now running")

        try:
            synced = await self.tree.sync()
            print(f"[BOT-INFO] Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    async def on_message(self, message):
        if message.author == self.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"[USER-INFO] {username} said '{user_message}' on channel {channel}")

        for mentioned_member in message.mentions:
            if mentioned_member.name == "DunkeyBot" and mentioned_member.bot is True:
                if "?" == message.content[-1]:
                    await message.reply("I invoke my right not to answer this question")
                else:
                    await message.reply("Who asked?")

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if self.voice_clients:
            bots_voice_client = discord.utils.get(self.voice_clients, guild=member.guild)
            if after.channel is None:
                if before.channel == bots_voice_client.channel:
                    num_of_members = len(bots_voice_client.channel.members)
                    if num_of_members == 1:
                        print("[BOT] The bot left the empty channel")
                        await bots_voice_client.disconnect()
            elif after.channel == bots_voice_client.channel:
                if len(after.channel.members) == 1:
                    print("[BOT] The bot left because it was moved to an empty channel")
                    await bots_voice_client.disconnect()


bot = DonkeyBot()


@bot.tree.command(name="join", description="join voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

        if voice and voice.is_connected():
            if voice.channel == channel:
                await interaction.response.send_message(
                    "`The bot is already on your channel`")
            else:
                await voice.move_to(channel)
                await interaction.response.send_message(
                    "`The bot has been moved to your channel`")
        else:
            voice = await channel.connect()
            await interaction.response.send_message(
                "`The bot has joined your channel`")
    else:
        await interaction.response.send_message(
            "`You are not in a voice channel.`")


@bot.tree.command(name="play", description="play some sound in a channel")
@discord.app_commands.describe(url="the link to the song")
async def play(interaction: discord.Interaction, url: str):
    guild = interaction.guild
    # VoiceClient associated with the specified guild (there is one bot per server)
    voice = discord.utils.get(bot.voice_clients, guild=guild)

    if voice and voice.is_connected():
        if voice.is_playing():
            await interaction.response.send_message("Sth is already playing")
            return
        else:
            await interaction.response.send_message("Here will be url info")

            # Use youtube-dl to extract the direct audio URL
            ydl_opts = {'format': 'bestaudio/best',
                        'postprocessors': [{'key': 'FFmpegExtractAudio',
                                            'preferredcodec': 'mp3'}]}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url = info['url']  # url to audio, there the audio data is in Opus format
                # Opus format - way of compressing and encoding the audio data

            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            voice.play(source)
    else:
        await interaction.response.send_message(
            "`The bot is not conencted to any channel`")


@bot.tree.command(name="loop", description="loop the audio")
@discord.app_commands.describe(url="the link to the song")
async def loop(interaction: discord.Interaction, url: str):
    bot.if_looped = True

    guild = interaction.guild
    # VoiceClient associated with the specified guild (there is one bot per server)
    voice = discord.utils.get(bot.voice_clients, guild=guild)

    if voice and voice.is_connected():
        if voice.is_playing():
            await interaction.response.send_message("Sth is already playing")
            return
        else:
            await interaction.response.send_message("Here will be url info")

            # Use youtube-dl to extract the direct audio URL
            ydl_opts = {'format': 'bestaudio/best',
                        'postprocessors': [{'key': 'FFmpegExtractAudio',
                                            'preferredcodec': 'mp3'}]}
            duration_sec = 0
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url = info['url']  # url to audio, there the audio data is in Opus format
                # Opus format - way of compressing and encoding the audio data
                duration_sec = info.get("duration", 0)

            while bot.if_looped:
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                voice.play(source)
                await asyncio.sleep(duration_sec + 1)
                # If voice (VoiceClient) was stopped during asyncio.sleep, another voice.stop(),
                # even thoough the voice has been already stopped, won't do anything
                voice.stop()
    else:
        await interaction.response.send_message(
            "`The bot is not conencted to any channel`")


@bot.tree.command(name='end_loop')
async def end_loop(interaction: discord.Interaction):
    bot.if_looped = False

    await interaction.response.send_message("Looping has been stopped")


@bot.tree.command(name='pause', description='pause the bot audio')
async def pause(interaction: discord.Interaction):
    voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if voice and voice.is_connected():
        if voice.is_playing():
            voice.pause()
            await interaction.response.send_message(
                "`The bot has been paused`")
        else:
            await interaction.response.send_message(
                "`The bot is currently not playing`")
    else:
        await interaction.response.send_message(
            "`The bot is not conencted to any channel`")


@bot.tree.command(name='resume', description="resume the bot's audio")
async def resume(interaction: discord.Interaction):
    voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if voice and voice.is_connected():
        if voice.is_paused():
            voice.resume()
            await interaction.response.send_message(
                "`The bot has been resumed`")
        else:
            if voice.is_playing():
                await interaction.response.send_message(
                    "`The bot is currently playing something`")
            else:
                await interaction.response.send_message(
                    "`The bot is currently not paused`")
    else:
        await interaction.response.send_message(
            "`The bot is not conencted to any channel`")


@bot.tree.command(name='stop', description="stop the bot's audio")
async def stop(interaction: discord.Interaction):
    voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if voice and voice.is_connected():
        if voice.is_playing():
            voice.stop()
            await interaction.response.send_message("`The bot has been stopped`")
        else:
            await interaction.response.send_message(
                "`You cannot stop the bot which is currently not playing`")
    else:
        await interaction.response.send_message(
            "`The bot is not conencted to any channel`")


@bot.tree.command(name='disconnect', description="disconnect the bot from the channel")
async def disconnect(interaction: discord.Interaction):
    voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        await interaction.response.send_message(
            "`The bot has been disconnect from your channel`")
    else:
        await interaction.response.send_message(
            "`The bot is not currently on any channel`")
