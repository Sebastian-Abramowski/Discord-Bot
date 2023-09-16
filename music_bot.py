import discord
import yt_dlp as youtube_dl
import asyncio
import utilities
from audio_queue import AudioQueue
from typing import Union, Tuple
from basic_bot import BasicBot

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


class MusicBot(BasicBot):
    def __init__(self):
        super().__init__()
        self.if_looped = False
        self.is_preparing_to_play = False
        self.if_queue_was_stopped = False
        self.if_skipped = False
        self.url_queue = AudioQueue()

    async def on_ready(self) -> None:
        await super().on_ready()
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(
                                       type=discord.ActivityType.listening, name="/play"))

    async def join(self, interaction: discord.Interaction, without_response=False) -> None:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

            await self.join_users_channel(interaction, bots_voice, channel,
                                          without_response)
        else:
            await self.respond_if_user_has_no_channel(interaction,
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

    async def respond_if_user_has_no_channel(self, interaction: discord.Interaction,
                                             without_response: bool) -> None:
        if not without_response:
            await interaction.response.send_message(
                "`You are not in a voice channel.`")

    async def play(self, interaction: discord.Interaction, url_or_search_query: Union[str, None],
                   if_play_next_in_queue=False) -> None:
        self.if_queue_was_stopped = False
        # VoiceClient associated with the specified guild (there is one bot per server)
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if not if_play_next_in_queue:
            await interaction.response.defer(thinking=True)

        if self.if_looped:
            msg = ("`The audio is looped currently. Use '/end_loop' "
                   "or '/stop' if you want it to stop.`")
            await self.respond_or_followup(
                interaction, msg)
            return None

        old_url_or_search_query = url_or_search_query
        url = None
        if url_or_search_query:
            url = self.get_validated_url(url_or_search_query, if_play_next_in_queue)
            if not url:
                await self.respond_or_followup(
                    interaction,
                    f"`Passed search query: \n{old_url_or_search_query}\ncouldn't be found`")
                return None

        if bots_voice and bots_voice.is_paused():
            self.url_queue.push(url)
            bots_voice.resume()
            msg = ("`Prioviosly paused bot was resumed and "
                   "the passed url was added to the queue`")
            await self.respond_or_followup(interaction, msg)
            return None

        if_bot_has_channel = await self.has_bot_joined_channel(interaction, bots_voice)
        if not if_bot_has_channel:
            await self.respond_or_followup(interaction, "`The user is not connected to any channel`")
            return None
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        # Managing queue
        if url and not if_play_next_in_queue:
            self.url_queue.push(url)
            if bots_voice.is_playing() or self.is_preparing_to_play:
                await self.respond_or_followup(interaction, "`Audio queue was updated`")
                return None
        if not if_play_next_in_queue:
            url = self.url_queue.pop()

        if bots_voice and bots_voice.is_connected():
            self.is_preparing_to_play = True
            if bots_voice.is_playing():
                await self.respond_or_followup(interaction, "`Something is already being played`")
                return None

            embed = await self.get_embed_message(interaction, url, "Currently playing: ")
            if not embed:
                await self.respond_or_followup(interaction, f"Currently playing: {url}")
            else:
                await self.respond_or_followup(interaction, message=None, embed=embed)

            url = self.extract_direct_audio_url(url)
            if not url:
                await self.respond_or_followup(
                    interaction,
                    "`Something went wrong with extracting audio URL...`")
                self.is_preparing_to_play = False
                return None

            await self.try_playing_audio_according_to_queue(interaction, bots_voice, url)
        else:
            await self.respond_or_followup(interaction, "`The bot is not conencted to any channel`")

    async def respond_or_followup(self, interaction: discord.Interaction, message: str,
                                  embed: discord.Embed = None) -> None:
        try:
            if not interaction.is_expired():
                await interaction.response.send_message(message, embed=embed)
        except discord.errors.InteractionResponded:
            if not interaction.is_expired():
                await interaction.followup.send(message, embed=embed)
        except Exception as e:
            print(e)

    def get_validated_url(self, url_or_search_query: str,
                          if_play_next_in_queue: bool) -> Union[str, None]:
        url = None
        if url_or_search_query and not if_play_next_in_queue:
            is_url_valid, _ = self.is_url_valid(url_or_search_query)
            if not is_url_valid:
                search_query = url_or_search_query
                url = self.get_url_from_search_query(search_query)
                return url
            else:
                url = url_or_search_query
                return url
        else:
            url = url_or_search_query
            return url

    def get_url_from_search_query(self, search_query: str) -> Union[str, None]:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Search for videos matching the query and get the URL of the first result
            search_results = ydl.extract_info(f'ytsearch:{search_query}', download=False)
            if 'entries' in search_results and len(search_results['entries']) > 0:
                video_url = search_results['entries'][0]['url']
                return video_url
            else:
                return None

    def is_url_valid(self, url: str) -> Tuple[bool, Union[str, None]]:
        # Returns bool indicating if url is valid and the massage about
        # what is wrong with url (it can be None)

        if self.is_url_youtube_playlist(url):
            return False, "`Passed url leads to youtube playlist. We advise to use single videos`"

        if not utilities.is_url_valid(url):
            return False, f"`You passed invalid url. Passed url: {url}`"
        return True, None

    def is_url_youtube_playlist(self, url: str) -> bool:
        return "youtube" in url and "list=" in url

    async def has_bot_joined_channel(self, interaction: discord.Interaction,
                                     bots_voice: discord.VoiceClient) -> bool:
        if not bots_voice:
            await self.join(interaction, without_response=True)
            bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

            # if there is still no voice connection that means that the user is in no channel
            if not bots_voice:
                return False
        return True

    def get_thumbnail_image_title_and_duration(self, url: str) -> Union[Tuple[str, str, int],
                                                                        Tuple[None, None, None]]:
        # Returns url to the thumbnail image, title and duration or None, None, None
        ydl_opts = {
                'quiet': True,
            }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                thumbnail_url = info_dict['thumbnail']
                duration = info_dict['duration']
                title = info_dict['title']

                return thumbnail_url, title, duration
        except Exception as e:
            print(e)
            return None, None, None

    async def get_embed_message(self, interaction: discord.Interaction, url: str,
                                message_at_the_top: str) -> Union[discord.Embed, None]:
        if interaction.is_expired():
            return None

        try:
            thumbnail_image_url, title, duration = self.get_thumbnail_image_title_and_duration(url)
            if not thumbnail_image_url and not title and not duration:
                return None
            embed = discord.Embed(colour=discord.Color.blue(), title=f"{title}")
            embed.set_author(name=message_at_the_top)
            embed.set_thumbnail(url=thumbnail_image_url)
            embed.add_field(name="Duration", value=f"{duration} s")
            potencial_next_qued_title = self.url_queue.get_first_one_to_leave()
            next_queued_title = potencial_next_qued_title if potencial_next_qued_title else "Nothing"
            embed.add_field(name="Next in queue", value=next_queued_title)
            embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
            return embed
        except Exception as e:
            print(e)
            return None

    def extract_direct_audio_url(self, url: str) -> Union[str, None]:
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

    async def try_playing_audio_according_to_queue(self, interaction: discord.Interaction,
                                                   bots_voice: discord.VoiceClient, url: str) -> None:
        try:
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            self.is_preparing_to_play = False
            bots_voice.play(source)

            while bots_voice.is_playing() or bots_voice.is_paused():
                await asyncio.sleep(0.2)

            if self.if_skipped:
                await self.respond_or_followup(interaction, "`Last song was skipped`")
                self.if_skipped = False
                return None

            if self.url_queue.queue and not self.if_queue_was_stopped:
                bots_voice.stop()
                await self.play(interaction, self.url_queue.pop(),
                                if_play_next_in_queue=True)
        except Exception as e:
            print(e)
            self.is_preparing_to_play = False
            self.if_queue_was_stopped = False
            await self.respond_or_followup(interaction,
                                           "`Something went wrong with playing audio...`")

    async def skip(self, interaction: discord.Interaction) -> None:
        if self.if_looped:
            msg = ("`You cannot skip a song that is playing in a loop. "
                   "If you want to end the loop, you should use '/end_loop' or '/stop'`")
            await interaction.response.send_message(msg)
            return None

        self.reset_attributes_without_queue_and_if_skipped()

        if self.url_queue.queue:
            bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
            if bots_voice.is_playing():
                await self.stop(interaction, without_response=True)
                self.if_skipped = True
                await self.play(interaction, url_or_search_query=None)
            else:
                await interaction.response.send_message(
                    "`The skip command was executed, but nothing is currently playing`")
        else:
            await interaction.response.send_message(
                "`Skip command was executed, but the audio queue is empty`")

    def reset_attributes_without_queue_and_if_skipped(self) -> None:
        self.if_looped = False
        self.is_preparing_to_play = False
        self.if_queue_was_stopped = False

    async def play_sui(self, interaction: discord.Interaction) -> None:
        await self.play_from_file(interaction, "Assets/sui.mp3", "SUUUUUUI")

    async def play_from_file(self, interaction: discord.Interaction, path_to_audio: str,
                             message_after_playing: str) -> None:
        if self.if_looped:
            await interaction.response.send_message(
                "`The audio is looped currently. Use '/end_loop' or '/stop' if you want it to stop.`")
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
                await self.try_playing_audio_from_file(interaction, bots_voice,
                                                       path_to_audio, message_after_playing)

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

    async def loop_audio(self, interaction: discord.Interaction, url_or_search_query: str) -> None:
        self.if_looped = True
        try:
            await interaction.response.defer(thinking=True)
        except Exception:
            pass  # interaction is already deferred

        url = None
        is_url_valid, _ = self.is_url_valid(url_or_search_query)
        if not is_url_valid:
            search_query = url_or_search_query
            url = self.get_url_from_search_query(search_query)
            await self.handle_loop_audio_request(interaction, url, search_query)
            return None
        else:
            url = url_or_search_query

        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
        if_bot_has_channel = await self.has_bot_joined_channel(interaction, bots_voice)
        if not if_bot_has_channel:
            await interaction.response.send_message("`The user is not connected to any channel`")
            return None
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            await self.play_audio_in_loop(interaction, bots_voice, url)

    async def handle_loop_audio_request(self, interaction: discord.Interaction,
                                        url: Union[str, None], search_query: str) -> None:
        self.if_looped = False
        if url:
            await self.loop_audio(interaction, url)
        else:
            await interaction.response.send_message(
                f"`Passed search query: \n{search_query}\ncouldn't be found`")

    async def play_audio_in_loop(self, interaction: discord.Interaction,
                                 bots_voice: discord.VoiceClient, url: str) -> None:
        if bots_voice.is_playing():
            await interaction.response.send_message("`Something is already playing`")
            return None

        embed = await self.get_embed_message(interaction, url, f"Currently looped: {url}")
        if not embed:
            await self.respond_or_followup(interaction, f"Currently looped: {url}")
        else:
            await self.respond_or_followup(interaction, message=None, embed=embed)

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
                await asyncio.sleep(0.2)

            # If voice (VoiceClient) was stopped during asyncio.sleep, another voice.stop(),
            # even though the voice has been already stopped, won't do anything
            bots_voice.stop()

    async def try_playing_from_direct_audio_url(self, bots_voice: discord.VoiceClient,
                                                url: str) -> bool:
        # Returns True if there was no errors, otherwise returns False
        try:
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            bots_voice.play(source)
            return True
        except Exception as e:
            print(e)
            return False

    async def end_loop(self, interaction: discord.Interaction) -> None:
        self.if_looped = False
        await interaction.response.send_message("`Looping has been stopped`")

    async def end_loop_now(self, interaction: discord.Interaction) -> None:
        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)

        if bots_voice and bots_voice.is_connected():
            await self.stop_bot_playing(interaction, bots_voice, without_response=True)
            self.if_queue_was_stopped = False
            await interaction.response.send_message("`The looping has been stopped immediately`")

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

    async def reset_bot(self, interaction: discord.Interaction,
                        without_response: bool = False) -> None:
        self.reset_attributes()

        bots_voice = discord.utils.get(self.voice_clients, guild=interaction.guild)
        if bots_voice and bots_voice.is_playing():
            bots_voice.stop()

        if not without_response:
            await interaction.response.send_message("The bot was reset")

    def reset_attributes(self) -> None:
        self.reset_attributes_without_queue_and_if_skipped()
        self.if_skipped = False
        self.url_queue = AudioQueue()

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


bot = MusicBot()


# Configurate slash commands
@bot.tree.command(name="join", description="Join voice channel of the caller")
async def join_command(interaction: discord.Interaction):
    await bot.join(interaction)


@bot.tree.command(name="play", description="Play some audio in the channel or add to the queue")
@discord.app_commands.describe(url_or_search_query="the link to the audio/video or yt search query")
async def play_command(interaciton: discord.Interaction, url_or_search_query: str):
    await bot.play(interaciton, url_or_search_query)


@bot.tree.command(name="loop", description="Loop the audio")
@discord.app_commands.describe(url_or_search_query="the link to the audio/video or search query")
async def loop_coomand(interaction: discord.Interaction, url_or_search_query: str):
    await bot.loop_audio(interaction, url_or_search_query)


@bot.tree.command(name="end_loop", description="End the loop, but keep the audio playing till the end")
async def end_loop_command(interaction: discord.Interaction):
    await bot.end_loop(interaction)


@bot.tree.command(name="end_loop_now", description="End the loop now")
async def end_loop_now_command(interaction: discord.Interaction):
    await bot.end_loop_now(interaction)


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
