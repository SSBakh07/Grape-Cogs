from typing import Literal

# TODO: clean up imports
import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import inline
import re

defaults = {
    "toggle": False
}

class TwtFixer(commands.Cog):
    """
    Ready Check
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot

        # Setting up persistent data
        self.config = Config.get_conf(
            self,
            identifier=1039588003770798192,
            force_registration=True,
        )
        self.config.register_guild(**defaults)


    def find_occurrence(self, msg):
        reg_str = "(https:\/\/)(twitter|x)(\.com\/)([a-zA-Z0-9_\/\?\=\&]+)"
        return re.findall(reg_str, msg)

    ##############################################
    
    @commands.group()
    async def twtfixer(self, ctx):
        """
            Command group for Twitter fixer
        """

    @twtfixer.command()
    async def help(self, ctx):
        await ctx.send("To be implemented")

    @twtfixer.command()
    async def toggle(self, ctx):
        async with self.config.guild(ctx.guild).toggle() as toggle:
            toggle = not toggle
            await ctx.send("TwtFixer set to: " + inline(str(toggle)))
    

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        async with self.config.guild(ctx.guild).toggle() as toggle:
            if not toggle or message.author == self.bot.user.id:
                return
            
            msg_content = message.content
            matches = self.find_occurrence(msg_content)
            if len(matches) > 0:
                for match in matches:
                    _match = list(match)
                    _match[1] = "vxtwitter"
                    await message.channel.send(''.join(_match))
                return