from typing import Literal

import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import inline, humanize_list
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.embed import randomize_colour
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

class ReadyCheck(commands.Cog):
    """
    Ready Check
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=1039588003770798192,
            force_registration=True,
        )
        # self.config.register_guild(**defaults)

    @commands.group(aliases=['readycheck'])
    @commands.guild_only()
    async def rc(self, ctx):
        """
            Group command for ready check
        """
        # TODO: add help

    @rc.command()
    async def test(self, ctx):
        """
            Publish test message
        """
        await ctx.send("Test message!")