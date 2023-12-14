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

    def construct_ban_embed(self, user, reason):
        embed = discord.Embed(title="User Banned")


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
    async def show(self, ctx, n_users=250):
        """
            List users banned by the server. Defaults to 250 users.
        """
        try:
            n_users = int(n_users)
        except:
            await ctx.send("Invalid value for `n_users`. Please enter a number")
            return

        # bans = await ctx.guild.bans()
        waiting_msg = await ctx.send("Please wait...")
        bans = [entry async for entry in ctx.guild.bans(limit=n_users)]

        ban_str = ""
        for ban in bans:
            ban_str += "- " + bold(ban.user.name) + f" (<@{ban.user.id}>)"
            if ban.reason:
                ban_str += ": " + italics(ban.reason)
            ban_str += "\n"
        
        embed_title = f"Users Banned from {ctx.guild.name}"
        
        raw_pages = [pg for pg in pagify(ban_str, page_length=1000)]
        pages = [italics(f"Page {i+1}/{len(raw_pages)}") + "\n\n" + pg for i, pg in enumerate(raw_pages)]
        embeds = [randomize_colour(discord.Embed(description=pg, title=embed_title)) for pg in pages]
        await menu(ctx, embeds, DEFAULT_CONTROLS)
        await waiting_msg.delete()


    @banlist.command()
    async def searchByUID(self, ctx, uid, n_users=250):
        """
            Find banned user by uid
        """
        if not uid:
            await ctx.send("User ID cannot be empty")
            return
        
        bans = [entry async for entry in ctx.guild.bans(limit=n_users)]
        await ctx.send("Has not been implemented yet!")





    @banlist.command()
    async def searchByUser(self, ctx):
        await ctx.send("Has not been implemented yet!")