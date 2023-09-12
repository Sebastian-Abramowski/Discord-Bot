import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import validations
from audio_queue import AudioQueue
from typing import Union, NoReturn

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


# commands.Bot is a subclass of discord.Client
class BasicBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='.', intents=discord.Intents.all())

    async def on_ready(self) -> None:
        print(f"[BOT-INFO] {self.user} is now running")

        await self.sync_commands_with_error_handling()

    async def sync_commands_with_error_handling(self) -> Union[None, NoReturn]:
        try:
            synced = await self.tree.sync()
            print(f"[BOT-INFO] Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return None

        self.print_message_info(message)

        for mentioned_member in message.mentions:
            if mentioned_member.name == "DonkeyBot" and mentioned_member.bot is True:
                await self.handle_reply_when_mentioned(message)

    def print_message_info(self, message: discord.Message) -> None:
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"[USER-INFO] {username} said '{user_message}' on channel {channel}")

    async def handle_reply_when_mentioned(self, message: discord.Message) -> None:
        if "?" == message.content[-1]:
            await message.reply("I invoke my right not to answer this question")
        else:
            await message.reply("Who asked?")

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:
        if self.voice_clients:
            bots_voice = discord.utils.get(self.voice_clients, guild=member.guild)
            if bots_voice:
                await self.disconnect_with_reset_when_bot_alone(bots_voice, before, after)

    async def disconnect_with_reset_when_bot_alone(self, bots_voice: discord.VoiceClient,
                                                   before: discord.VoiceState,
                                                   after: discord.VoiceState) -> None:
        if_bots_channel_changed = (before.channel == bots_voice.channel or
                                   after.channel == bots_voice.channel)
        if if_bots_channel_changed:
            num_of_members = len(bots_voice.channel.members)
            if num_of_members == 1:
                print("[BOT] The bot left the empty channel")
                await bots_voice.disconnect()
                self.reset_attributes()

    def reset_attributes(self) -> None:
        info = ("[POTENCIAL-PROBLEM] If your bot have some additional "
                "attributes that you want to reset "
                "after disconnecting the bot, then you should "
                "overwrite 'reset_attributes' method...")
        print(info)


class MusicBot(BasicBot):
    def __init__(self):
        super().__init__()
        self.if_looped = False
        self.is_preparing_to_play = False
        self.if_queue_was_stopped = False
        self.if_skipped = False
        self.url_queue = AudioQueue()

    async def join(self, interaction: discord.Interaction, without_response=False) -> None:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

            await self.join_users_channel(interaction, bots_voice, channel,
                                          without_response)
        else:
            await self.response_if_user_has_no_channel(interaction,
                                                       without_response)

    async def join_users_channel(self, interaction: discord.Interaction,
                                 bots_voice: discord.VoiceClient,
                                 channel: discord.VoiceChannel, without_response: bool) -> None:
        if bots_voice and bots_voice.is_connected():
            await self.move_to_users_channel(interaction, bots_voice, channel,
                                             without_response)
        else:
            await self.connect_to_users_channel(interaction, channel,
                                                without_response)

    async def move_to_users_channel(self, interaction: discord.Interaction,
                                    bots_voice: discord.VoiceClient,
                                    channel: discord.VoiceChannel, without_response: bool) -> None:
        if bots_voice.channel == channel:
            if not without_response:
                await interaction.response.send_message(
                    "`The bot is already on your channel`")
        else:
            await bots_voice.move_to(channel)
            if not without_response:
                await interaction.response.send_message(
                    "`The bot has been moved to your channel`")

    async def connect_to_users_channel(self, interaction: discord.Interaction,
                                       channel: discord.VoiceChannel,
                                       without_response: bool) -> None:
        await channel.connect()
        if not without_response:
            await interaction.response.send_message(
                "`The bot has joined your channel`")

    async def response_if_user_has_no_channel(self, interaction: discord.Interaction,
                                              without_response: bool) -> None:
        if not without_response:
            await interaction.response.send_message(
                "`You are not in a voice channel.`")

    async def play(self, interaction: discord.Interaction, url: Union[str, None],
                   if_next_in_queue=False, if_skipped=False) -> None:
        self.if_queue_was_stopped = False
        # VoiceClient associated with the specified guild (there is one bot per server)
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if self.if_looped:
            await self.respond_or_followup(
                interaction, "`The audio is looped currently. Use /end_loop if you want it to stop.`")
            return None

        # If if_next_in_queue is True, that means the url was already validated
        if not if_next_in_queue:
            if url and self.is_url_youtube_playlist(url):
                await self.respond_or_followup(
                    interaction,
                    "`Passed url leads to youtube playlist. We advise to use single videos`")
                return None

            if url and not validations.is_url_valid(url):
                await self.respond_or_followup(interaction,
                                               f"`You passed invalid url. Passed url: {url}`")
                return None

        if bots_voice and bots_voice.is_paused():
            self.url_queue.push(url)
            bots_voice.resume()
            response_msg = ("`Prioviosly paused bot was resumed and "
                            "the passed url was added to the queue`")
            await self.respond_or_followup(interaction, response_msg)
            return None

        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
        if_bot_has_channel = await self.has_bot_joined_channel(interaction, bots_voice)
        if not if_bot_has_channel:
            await self.respond_or_followup(interaction, "`The user is not connected to any channel`")
            return None
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        # Managing queue
        if url and not if_next_in_queue:
            self.url_queue.push(url)
            if bots_voice.is_playing() or self.is_preparing_to_play:
                await self.respond_or_followup(interaction, "`Audio queue was updated`")
                return None
        if not if_next_in_queue:
            url = self.url_queue.pop()

        if bots_voice and bots_voice.is_connected():
            self.is_preparing_to_play = True
            if bots_voice.is_playing():
                await self.respond_or_followup(interaction, "`Something is already being played`")
                return None
            else:
                await self.respond_or_followup(interaction, f"Currently playing: {url}")

                # Use youtube-dl to extract the direct audio URL
                ydl_opts = {'format': 'bestaudio/best',
                            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                                'preferredcodec': 'mp3'}]}
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        url = info['url']  # url to audio, there the audio data is in Opus format
                        # Opus format - way of compressing and encoding the audio data
                except Exception as e:
                    print(e)
                    await self.respond_or_followup(
                        interaction,
                        "`Something went wrong with extracting audio URL...`")
                    self.is_preparing_to_play = False
                    return None

                try:
                    source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                    self.is_preparing_to_play = False
                    bots_voice.play(source)

                    while bots_voice.is_playing() or bots_voice.is_paused():
                        await asyncio.sleep(1)

                    if self.if_skipped:
                        await self.respond_or_followup(interaction, "`Last song was skipped`")
                        self.if_skipped = False
                        return None

                    if self.url_queue.queue and not self.if_queue_was_stopped:
                        bots_voice.stop()

                        await self.play(interaction, self.url_queue.pop(),
                                        if_next_in_queue=True)
                except Exception as e:
                    print(e)
                    await self.respond_or_followup(interaction,
                                                   "`Something went wrong with playing audio...`")
                    self.is_preparing_to_play = False
                    self.if_queue_was_stopped = False
        else:
            await self.respond_or_followup(interaction, "`The bot is not conencted to any channel`")

    async def respond_or_followup(self, interaction: discord.Interaction, message: str) -> None:
        try:
            await interaction.response.send_message(message)
        except discord.errors.InteractionResponded:
            await interaction.followup.send(message)

    async def skip(self, interaction: discord.Interaction) -> None:
        if self.if_looped:
            msg = ("`You cannot skip a song that is playing in a loop. "
                   "If you want to end the loop, you should use '/end_loop' or '/stop'`")
            await interaction.response.send_message(msg)
            return None

        await self.stop(interaction, without_response=True)
        self.reset_attributes_without_queue_and_if_skipped()

        if self.url_queue.queue:
            bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
            if bots_voice.is_playing():
                self.if_skipped = True
                await self.play(interaction, url=None)
            else:
                await interaction.response.send_message(
                    "'The skip command was executed, but nothing is currently playing'")
        else:
            await interaction.response.send_message(
                "`Skip command was executed, but the audio queue is empty`")

    async def play_sui(self, interaction: discord.Interaction) -> None:
        await self.play_from_file(interaction, "Assets/sui.mp3", "SUUUUUUI")

    async def play_from_file(self, interaction: discord.Interaction, path_to_audio: str,
                             message_after_playing: str) -> None:
        if self.if_looped:
            await interaction.response.send_message(
                "`The audio is looped currently. Use /end_loop if you want it to stop.`")
            return None

        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
        if_bot_has_channel = await self.has_bot_joined_channel(interaction, bots_voice)
        if not if_bot_has_channel:
            await interaction.response.send_message("`The user is not connected to any channel`")
            return None
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        await self.play_audio_from_file(interaction, bots_voice, path_to_audio,
                                        message_after_playing)

    async def play_audio_from_file(self, interaction: discord.Interaction,
                                   bots_voice: discord.VoiceClient,
                                   path_to_audio: str, message_after_playing: str) -> None:
        if bots_voice and bots_voice.is_connected():
            if bots_voice.is_playing():
                await interaction.response.send_message(
                    "`The bot is currently playing something`")
            else:
                await self.try_playing_audio_from_file(interaction, bots_voice, path_to_audio,
                                                       message_after_playing)

    async def try_playing_audio_from_file(self, interaction: discord.Interaction,
                                          bots_voice: discord.VoiceClient,
                                          path_to_audio: str, message_after_playing: str) -> None:
        try:
            source = discord.FFmpegOpusAudio(path_to_audio)
            bots_voice.play(source)
            await interaction.response.send_message(message_after_playing)
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                f"`There was a problem with playing {path_to_audio} audio file`")

    async def has_bot_joined_channel(self, interaction: discord.Interaction,
                                     bots_voice: discord.VoiceClient) -> bool:
        if not bots_voice:
            await self.join(interaction, without_response=True)
            bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

            # if there is still no voice connection that means that the user is in no channel
            if not bots_voice:
                return False
        return True

    async def loop_audio(self, interaction: discord.Interaction, url: str) -> None:
        self.if_looped = True

        if self.is_url_youtube_playlist(url):
            await interaction.response.send_message(
                "`Passed url leads to youtube playlist. We advise to use single videos`")
            return None

        if not validations.is_url_valid(url):
            await interaction.response.send_message(f"`You passed invalid url. Passed url: {url}`")
            return None

        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
        if_bot_has_channel = await self.has_bot_joined_channel(interaction, bots_voice)
        if not if_bot_has_channel:
            await interaction.response.send_message("`The user is not connected to any channel`")
            return None
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            await self.play_audio_in_loop(interaction, bots_voice, url)

    async def play_audio_in_loop(self, interaction: discord.Interaction,
                                 bots_voice: discord.VoiceClient, url: str) -> None:
        if bots_voice.is_playing():
            await interaction.response.send_message("`Something is already playing`")
            return None

        await interaction.response.send_message(f"Currently looped: {url}")

        url = self.extract_direct_audio_url(url)
        if not url:
            await interaction.followup.send(
                "`Something went wrong with extracting audio URL...`")
            return None

        while self.if_looped:
            if_played_without_errors = await self.try_playing_from_direct_audio_url(bots_voice,
                                                                                    url)
            if not if_played_without_errors:
                await interaction.followup.send(
                    "`Something went wrong with playing audio...`")
                return None

            while bots_voice.is_playing():
                await asyncio.sleep(1)

            # If voice (VoiceClient) was stopped during asyncio.sleep, another voice.stop(),
            # even though the voice has been already stopped, won't do anything
            bots_voice.stop()

    async def try_playing_from_direct_audio_url(self, bots_voice: discord.VoiceClient, url: str) -> bool:
        # Returns True if there was no errors, otherwise False

        try:
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            bots_voice.play(source)
            return True
        except Exception as e:
            print(e)
            return False

    def extract_direct_audio_url(self, url: str) -> Union[str, None]:
        # Use youtube-dl to extract the direct audio URL
        ydl_opts = {'format': 'bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio',
                                        'preferredcodec': 'mp3'}]}
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url = info['url']  # url to audio, there the audio data is in Opus format
                # Opus format - way of compressing and encoding the audio data
                return url
        except Exception as e:
            print(e)
            return None

    def is_url_youtube_playlist(self, url: str) -> bool:
        return "youtube" in url and "list=" in url

    async def end_loop(self, interaction: discord.Interaction) -> None:
        self.if_looped = False
        await interaction.response.send_message("`Looping has been stopped`")

    async def pause(self, interaction: discord.Interaction) -> None:
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            await self.pause_bot_playing(interaction, bots_voice)
        else:
            await interaction.response.send_message(
                "`The bot is not conencted to any channel`")

    async def pause_bot_playing(self, interaction: discord.Interaction,
                                bots_voice: discord.VoiceClient) -> None:
        if bots_voice.is_playing():
            bots_voice.pause()
            await interaction.response.send_message(
                "`The bot has been paused`")
        else:
            await interaction.response.send_message(
                "`The bot is currently not playing`")

    async def resume(self, interaction: discord.Interaction) -> None:
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            await self.resume_paused_bot(interaction, bots_voice)
        else:
            await interaction.response.send_message(
                "`The bot is not conencted to any channel`")

    async def resume_paused_bot(self, interaction: discord.Interaction,
                                bots_voice: discord.VoiceClient) -> None:
        if bots_voice.is_paused():
            bots_voice.resume()
            await interaction.response.send_message(
                "`The bot has been resumed`")
        else:
            await self.send_response_after_resume_when_not_paused(interaction, bots_voice)

    async def send_response_after_resume_when_not_paused(self, interaction: discord.Interaction,
                                                         bots_voice: discord.VoiceClient) -> None:
        if bots_voice.is_playing():
            await interaction.response.send_message(
                "`The bot is currently playing something`")
        else:
            await interaction.response.send_message(
                "`The bot is currently not paused`")

    async def stop(self, interaction: discord.Interaction, without_response=False) -> None:
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            await self.stop_bot_playing(interaction, bots_voice, without_response)
        else:
            if not without_response:
                await interaction.response.send_message(
                    "`The bot is not conencted to any channel`")

    async def stop_bot_playing(self, interaction: discord.Interaction,
                               bots_voice: discord.VoiceClient, without_response: bool) -> None:
        if bots_voice.is_playing():
            bots_voice.stop()
            self.if_queue_was_stopped = True
            self.if_looped = False
            if not without_response:
                await interaction.response.send_message("`The bot has been stopped`")
        else:
            if not without_response:
                await interaction.response.send_message(
                    "`You cannot stop the bot which is currently not playing`")

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

    async def put_on_top_of_queue(self, interaction: discord.Interaction, url: str) -> None:
        self.url_queue.push_with_priority(url)
        await interaction.response.send_message("`Item was put on the top of the audio queue`")

    def reset_attributes_without_queue_and_if_skipped(self) -> None:
        self.if_looped = False
        self.is_preparing_to_play = False
        self.if_queue_was_stopped = False

    def reset_attributes(self) -> None:
        self.reset_attributes_without_queue_and_if_skipped()
        self.if_skipped = False
        self.url_queue = AudioQueue()

    async def reset_bot(self, interaction: discord.Interaction,
                        without_response: bool = False) -> None:
        self.reset_attributes()

        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
        if bots_voice and bots_voice.is_playing():
            bots_voice.stop()

        if not without_response:
            await interaction.response.send_message("The bot was reset")

    async def disconnect(self, interaction: discord.Interaction) -> None:
        await self.reset_bot(interaction, without_response=True)

        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
        if bots_voice and bots_voice.is_connected():
            await bots_voice.disconnect()
            await interaction.response.send_message(
                "`The bot has been disconnect from your channel`")
        else:
            await interaction.response.send_message(
                "`The bot is not currently on any channel`")


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
    # TODO: check_movie movie
    # TODO: check_marvel_character
    # TODO: check_marvel_film # https://developer.marvel.com/docs


class DonkeyBot(MusicBot, RandomBot):
    def __init__(self):
        super().__init__()

    # TODO: check_eng_word
    # TODO: weather where


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


@bot.tree.command(name="disconnect", description="Disconnect the bot from the channel with reset")
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


@bot.tree.command(name="put_on_top_of_queue", description="Put item on the top of the audio queue")
@discord.app_commands.describe(url="the link to the audio/video")
async def put_on_top_of_queue_command(interaction: discord.Interaction, url: str):
    await bot.put_on_top_of_queue(interaction, url)


@bot.tree.command(name="reset_bot", description="Reset the bot")
async def reset_command(interaction: discord.Interaction):
    await bot.reset_bot(interaction)


@bot.tree.command(name="skip", description="Skip current audio and continue with the queue")
async def skip_command(interaction: discord.Interaction):
    await bot.skip(interaction)


@bot.tree.command(name="play_sui", description="Play sui")
async def play_sui_command(interaction: discord.Interaction):
    await bot.play_sui(interaction)


@bot.tree.command(name="test_random", description="TESTING")
async def test_random_command(interaction: discord.Interaction):
    await bot.test_random(interaction)


# TODO: hosting
# TODO: sprawdź type hinty
# TODO: poczytaj o API
# TODO: podział na dwa różne boty
