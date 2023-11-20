from typing import Literal

# TODO: clean up imports
import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import inline
from redbot.core.utils.embed import randomize_colour
import re

class TwtFilter(commands.Cog):
    """
    Tweet filter
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

    def find_occurrence_twt(self, msg):
        reg_str = "(https:\/\/)(twitter|x)(\.com\/)([a-zA-Z0-9_\/\?\=\&]+)"
        return re.findall(reg_str, msg)
    

    ##############################################
    
    @commands.group(alias=["tf"])
    async def twtfilter(self, ctx):
        """
            Command group for twitter filter
        """

    @twtfilter.command()
    async def help(self, ctx):
        """
            Help on how to use this cog
        """
        await ctx.send("To be implemented")
        

    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    #     # Add