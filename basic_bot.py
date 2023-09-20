import discord
from discord.ext import commands
import os


# commands.Bot is a subclass of discord.Client
class BasicBot(commands.Bot):
    def __init__(self, name: str):
        super().__init__(command_prefix='.', intents=discord.Intents.all())
        self.name = name

    async def on_ready(self) -> None:
        print(f"[BOT-INFO] {self.user} is now running")

        await self.sync_commands_with_error_handling()

    async def sync_commands_with_error_handling(self) -> None:
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
            if mentioned_member.name == self.name and mentioned_member.bot is True:
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
            embed = discord.Embed(color=discord.Color.dark_green(), title="Who asked?")
            file = discord.File(os.path.join("Assets", "broccoli.png"), filename="broccoli.png")
            embed.set_image(url="attachment://broccoli.png")
            await message.reply(file=file, embed=embed)

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
