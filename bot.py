import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from audio_queue import AudioQueue
from other import is_url_valid

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


# commands.Bot is subclass of discord.Client
class DonkeyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='.', intents=discord.Intents.all())
        self.if_looped = False
        self.is_preparing_to_play = False
        self.if_queue_was_stopped = False
        self.url_queue = AudioQueue()

    async def on_ready(self) -> None:
        print(f"[BOT-INFO] {self.user} is now running")

        try:
            synced = await self.tree.sync()
            print(f"[BOT-INFO] Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return None

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"[USER-INFO] {username} said '{user_message}' on channel {channel}")

        for mentioned_member in message.mentions:
            if mentioned_member.name == "DonkeyBot" and mentioned_member.bot is True:
                if "?" == message.content[-1]:
                    await message.reply("I invoke my right not to answer this question")
                else:
                    await message.reply("Who asked?")

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:
        if self.voice_clients:
            bots_voice = discord.utils.get(self.voice_clients, guild=member.guild)
            if after.channel is None:
                if before.channel == bots_voice.channel:
                    num_of_members = len(bots_voice.channel.members)
                    if num_of_members == 1:
                        print("[BOT] The bot left the empty channel")
                        await bots_voice.disconnect()
            elif after.channel == bots_voice.channel:
                if member.bot and len(after.channel.members) == 1:
                    print("[BOT] The bot left because it was moved to an empty channel")
                    await bots_voice.disconnect()

    async def join(self, interaction: discord.Interaction) -> None:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

            if bots_voice and bots_voice.is_connected():
                if bots_voice.channel == channel:
                    await interaction.response.send_message(
                        "`The bot is already on your channel`")
                else:
                    await bots_voice.move_to(channel)
                    await interaction.response.send_message(
                        "`The bot has been moved to your channel`")
            else:
                bots_voice = await channel.connect()
                await interaction.response.send_message(
                    "`The bot has joined your channel`")
        else:
            await interaction.response.send_message(
                "`You are not in a voice channel.`")

    async def play(self, interaction: discord.Interaction, url: str,
                   if_next_in_queue=False) -> None:
        self.if_queue_was_stopped = False

        guild = interaction.guild
        # VoiceClient associated with the specified guild (there is one bot per server)
        bots_voice = discord.utils.get(self.voice_clients, guild=guild)

        if not is_url_valid(url):
            await interaction.followup.send(f"`You passed invalid url. Passed url: {url}`")
            return None
        else:
            self.url_queue.push(url)
            if bots_voice.is_playing() or self.is_preparing_to_play:
                if if_next_in_queue:
                    await interaction.followup.send("`Audio queue was updated`")
                else:
                    await interaction.response.send_message("`Audio queue was updated`")
                return None
            self.is_preparing_to_play = True
            url = self.url_queue.pop()

        if bots_voice and bots_voice.is_connected():
            if bots_voice.is_playing():
                if if_next_in_queue:
                    await interaction.followup.send("`Something is already being played`")
                else:
                    await interaction.response.send_message("`Something is already being played`")
                return None
            else:
                if if_next_in_queue:
                    await interaction.followup.send(f"Currently playing: {url}")
                else:
                    await interaction.response.send_message(f"Currently playing: {url}")

                # Use youtube-dl to extract the direct audio URL
                ydl_opts = {'format': 'bestaudio/best',
                            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                                'preferredcodec': 'mp3'}]}
                duration_sec = 0
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        url = info['url']  # url to audio, there the audio data is in Opus format
                        # Opus format - way of compressing and encoding the audio data
                        duration_sec = info.get("duration", 0)
                except Exception as e:
                    print(e)
                    await interaction.followup.send(
                        "`Something went wrong with extracting audio URL...`")
                    return None

                try:
                    source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                    bots_voice.play(source)
                    self.is_preparing_to_play = False

                    if duration_sec > 0:
                        await asyncio.sleep(duration_sec + 1)
                        if self.url_queue.queue and not self.if_queue_was_stopped:
                            bots_voice.stop()

                            await self.play(interaction, self.url_queue.pop(),
                                            if_next_in_queue=True)
                    else:
                        await interaction.followup.send(
                            "`Something went wrong with reading the video length, " +
                            "the queue stopped playing...`")

                except Exception as e:
                    print(e)
                    await interaction.followup.send("`Something went wrong with playing audio...`")
        else:
            if if_next_in_queue:
                await interaction.followup.send(
                    "`The bot is not conencted to any channel`")
            else:
                await interaction.response.send_message(
                    "`The bot is not conencted to any channel`")

    async def loop_audio(self, interaction: discord.Interaction, url: str) -> None:
        self.if_looped = True

        guild = interaction.guild
        # VoiceClient associated with the specified guild (there is one bot per server)
        bots_voice = discord.utils.get(self.voice_clients, guild=guild)

        if bots_voice and bots_voice.is_connected():
            if bots_voice.is_playing():
                await interaction.response.send_message("`Something is already playing`")
                return None
            else:
                await interaction.response.send_message(f"Currently looped: {url}")

                if not is_url_valid(url):
                    await interaction.followup.send(f"`You passed invalid url. Passed url: {url}`")
                    return None

                # Use youtube-dl to extract the direct audio URL
                ydl_opts = {'format': 'bestaudio/best',
                            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                                'preferredcodec': 'mp3'}]}
                duration_sec = 0
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        url = info['url']  # url to audio, there the audio data is in Opus format
                        # Opus format - way of compressing and encoding the audio data
                        duration_sec = info.get("duration", 0)
                except Exception as e:
                    print(e)
                    await interaction.followup.send(
                        "`Something went wrong with extracting audio URL...`")
                    return None

                while self.if_looped:
                    # Turn off looping when the duration was read not correctly
                    if duration_sec == 0:
                        self.if_looped = False

                    try:
                        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                        bots_voice.play(source)
                    except Exception as e:
                        print(e)
                        await interaction.followup.send(
                            "`Something went wrong with playing audio...`")

                    await asyncio.sleep(duration_sec + 1)
                    # If voice (VoiceClient) was stopped during asyncio.sleep, another voice.stop(),
                    # even thoough the voice has been already stopped, won't do anything
                    bots_voice.stop()
        else:
            await interaction.response.send_message(
                "`The bot is not conencted to any channel`")

    async def end_loop(self, interaction: discord.Interaction) -> None:
        self.if_looped = False
        await interaction.response.send_message("`Looping has been stopped`")

    async def pause(self, interaction: discord.Interaction) -> None:
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            if bots_voice.is_playing():
                bots_voice.pause()
                await interaction.response.send_message(
                    "`The bot has been paused`")
            else:
                await interaction.response.send_message(
                    "`The bot is currently not playing`")
        else:
            await interaction.response.send_message(
                "`The bot is not conencted to any channel`")

    async def resume(self, interaction: discord.Interaction) -> None:
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            if bots_voice.is_paused():
                bots_voice.resume()
                await interaction.response.send_message(
                    "`The bot has been resumed`")
            else:
                if bots_voice.is_playing():
                    await interaction.response.send_message(
                        "`The bot is currently playing something`")
                else:
                    await interaction.response.send_message(
                        "`The bot is currently not paused`")
        else:
            await interaction.response.send_message(
                "`The bot is not conencted to any channel`")

    async def stop(self, interaction: discord.Interaction) -> None:
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            if bots_voice.is_playing():
                bots_voice.stop()
                self.if_queue_was_stopped = True
                self.if_looped = False
                await interaction.response.send_message("`The bot has been stopped`")
            else:
                await interaction.response.send_message(
                    "`You cannot stop the bot which is currently not playing`")
        else:
            await interaction.response.send_message(
                "`The bot is not conencted to any channel`")

    async def disconnect(self, interaction: discord.Interaction) -> None:
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            await bots_voice.disconnect()
            await interaction.response.send_message(
                "`The bot has been disconnect from your channel`")
        else:
            await interaction.response.send_message(
                "`The bot is not currently on any channel`")

    async def show_queue(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(str(self.url_queue))

    async def clear_queue(self, interaction: discord.Interaction) -> None:
        if self.url_queue.queue:
            self.url_queue.clear()
            await interaction.response.send_message("`The queue was cleared`")
        else:
            await interaction.response.send_message("`The queue is already empty`")

    async def shuffle_queue(self, interaction: discord.Interaction) -> None:
        if self.url_queue.queue:
            self.url_queue.shuffle()
            await interaction.response.send_message("`The queue was shuffled`")
        else:
            await interaction.response.send_message("`You try to shuffle the empty queue`")


bot = DonkeyBot()


# Configurate slash commands
@bot.tree.command(name="join", description="Join voice channel of the caller")
async def join_command(interaction: discord.Interaction):
    await bot.join(interaction)


@bot.tree.command(name="play", description="Play some audio in the channel")
@discord.app_commands.describe(url="the link to the audio/video")
async def play_command(interaciton: discord.Interaction, url: str):
    await bot.play(interaciton, url)


@bot.tree.command(name="loop", description="Loop the audio")
@discord.app_commands.describe(url="the link to the audio/video")
async def loop_coomand(interaction: discord.Interaction, url: str):
    await bot.loop_audio(interaction, url)


@bot.tree.command(name="end_loop", description="End the loop")
async def end_loop_command(interaction: discord.Interaction):
    await bot.end_loop(interaction)


@bot.tree.command(name="pause", description="Pause the bot's currently playing audio")
async def pause_command(interaction: discord.Interaction):
    await bot.pause(interaction)


@bot.tree.command(name="resume", description="Resume the bot's audio")
async def resume_command(interaction: discord.Interaction):
    await bot.resume(interaction)


@bot.tree.command(name="stop", description="Stop the bot's audio")
async def stop_command(interaction: discord.Interaction):
    await bot.stop(interaction)


@bot.tree.command(name="disconnect", description="Disconnect the bot from the channel")
async def disconnect_command(interaction: discord.Interaction):
    await bot.disconnect(interaction)


@bot.tree.command(name="show_queue", description="Shows the audio queue")
async def show_queue_command(interaction: discord.Interaction):
    await bot.show_queue(interaction)


@bot.tree.command(name="clear_queue", description="Clear the audio queue")
async def clear_queue_command(interaction: discord.Interaction):
    await bot.clear_queue(interaction)


@bot.tree.command(name="shuffle_queue", description="Shuffle the audio queue")
async def shuffle_queue_command(interaction: discord.Interaction):
    await bot.shuffle_queue(interaction)
