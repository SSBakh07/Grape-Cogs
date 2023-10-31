from typing import Literal

# TODO: clean up imports
import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import inline
import re



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
        # self.config.register_guild(**defaults)

        self.toggle = False


    def find_occurrence(self, msg):
        reg_str = "(https:\/\/)?(twitter|x)(\.com\/)?([a-zA-Z0-9_\/\?\=\&]+)"
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
        self.toggle = not self.toggle
        await ctx.send("TwtFixer set to: " + inline(str(self.toggle)))
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.toggle:
            return
        
        msg_content = message.content
        matches = self.find_occurrence(msg_content)
        if len(matches) > 0:
            await message.channel.send(str(matches))
            return


    
    