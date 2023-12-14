from typing import Literal

# TODO: clean up imports
import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import inline, italics, pagify, bold
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.embed import randomize_colour
from redbot.core.utils.predicates import MessagePredicate
import re

class BanList(commands.Cog):
    """
    Ban List
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


    ##############################################

    @checks.admin_or_permissions(ban_members=True)
    @commands.group(aliases=["bl"])
    async def banlist(self, ctx):
        """
            Command group for the banlist cog
        """


    @banlist.command()
    async def help(self, ctx):
        """
            Help on how to use this cog
        """
        await ctx.send("Not implemented yet!")

    @banlist.command()
    async def show(self, ctx):
        """
            List users banned by the server
        """
        # bans = await ctx.guild.bans()
        waiting_msg = await ctx.send("Please wait...")
        bans = [entry async for entry in ctx.guild.bans(limit=None)]

        ban_str = ""
        for ban in bans:
            ban_str += "- " + bold(ban.user.name) + "(" + str(ban.user.id) + "): " + italics(ban.reason) + "\n"
        

        pages = pagify(ban_str)
        await menu(ctx, pages, DEFAULT_CONTROLS)
        await waiting_msg.delete()

    @banlist.command()
    async def searchByUID(self, ctx):
        await ctx.send("Has not been implemented yet!")

    @banlist.command()
    async def searchByUser(self, ctx):
        await ctx.send("Has not been implemented yet!")