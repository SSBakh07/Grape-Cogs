from typing import Literal

import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import inline, humanize_list
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.embed import randomize_colour
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.views import ConfirmView
import asyncio
from CheckView import CheckView
# https://stackoverflow.com/questions/62507316/executing-a-function-after-a-certain-period-of-time (asyncio)

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Button",style=discord.ButtonStyle.green)
    async def green_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(content=f"This is an edited button response!")
        self.stop()
        # respond to the interaction so the user does not see "interaction failed".
        await interaction.response.defer()
        # call `on_timeout` explicitly here since it's not called when `stop()` is called.
        await self.on_timeout()



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
        # msg = await ctx.send("Test message!", view=Buttons())
        view = CheckView()

        view.message = await ctx.send("Are you sure you about that?", view=view)
        await view.wait()

        final_msg = " ".join([str(id) for id in view.interacted_users])
        await ctx.send(final_msg)

        