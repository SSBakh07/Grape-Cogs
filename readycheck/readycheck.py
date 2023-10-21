from typing import Literal

# TODO: clean up imports
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
from .CheckView import CheckView
import time
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

# TODO: make customizable
react_emoji = "✅"
time_to_wait = 60.0

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


    def parse_time(self, timestring):
        """
            Get discord-friendly timestamp from relative string. Inputs are relative e.g. "15 minutes", "1 hour", "30 seconds", etc.
        """
        try:
            alpha_idx = timestring.find(next(filter(str.isalpha, timestring)))
            number = int(timestring[:alpha_idx])
            timeframe = str(timestring[alpha_idx:])
        except:
            return -1, -1
        

        unix_timestamp = time.time()
        
        # TODO: fix bug w space
        # https://discord.com/channels/1020788106951143474/1076594655052976323/1165276098993590332
        if timeframe[0] == 'm':
            wait_time = number * 60
        elif timeframe[0] == 'h':
            wait_time = number * 60 * 60
        else:
            wait_time = number

        unix_timestamp += wait_time
        return unix_timestamp, wait_time

    
    @rc.command()
    async def create(self, ctx, create_time):
        """
            Create a ready check.
        """

        parsed_time, wait_time = self.parse_time(create_time)
        if parsed_time == -1:
            ctx.send("Invalid time format. Try something like '15 minutes' or '1hr' or something.")
            return

        msg_content = "Ready check <t:{}:R>.\nReact with {} to be notified when it starts!".format(str(int(parsed_time)), react_emoji)
        prep_embed = discord.Embed(title="Ready Check", description=msg_content, color=discord.Colour.blurple())
        prep_msg = await ctx.send(embed=prep_embed)
        await prep_msg.add_reaction("{}".format(react_emoji))


        await asyncio.sleep(wait_time)
        await prep_msg.remove_reaction("{}".format(react_emoji), self.bot.user)

        # Get and parse reactions
        prep_msg = await ctx.fetch_message(prep_msg.id)
        users = set()

        #     # TODO: add check
        #     # if reaction.emoji == react_emoji:
        for reaction in prep_msg.reactions:
            async for user in reaction.users():
                users.add(user)

        # Delete original prep message
        await prep_msg.delete()

        # await ctx.send("Readycheck here!")
        # await ctx.send(f"users: {', '.join(user.name for user in users)}")

        waiting_users = [user.id for user in users]


        # Send final ready check message
        users_str = " ".join(["<@{}>".format(str(uid)) for uid in waiting_users])
        msg_content = "Hit the {} react below to indicate you're ready!".format(react_emoji)
        users_embed = discord.Embed(title="Ready Check", description=msg_content, color=discord.Colour.blue())
        await ctx.send(embed = users_embed)


        users_msg = await ctx.send("Waiting on: {}".format(users_str))
        await users_msg.add_reaction("{}".format(react_emoji))

        now = time.time()
        deadline = now + time_to_wait
        ready_users = []

        # Keep checking reacts with an interval of 0.5 sec
        while time.time() < deadline and len(waiting_users) > 0:
            await asyncio.sleep(0.5)

            # Get reacts to message
            users_msg = await ctx.fetch_message(users_msg.id)

            #     # TODO: add check
            #     # if reaction.emoji == react_emoji:
            for reaction in users_msg.reactions:
                async for user in reaction.users():
                    if user.id in waiting_users:
                        waiting_users.remove(user.id)
                        ready_users.append(user.id)

                        users_str = " ".join(["<@{}>".format(str(uid)) for uid in waiting_users])
                        msg_content = "Waiting on: {}".format(users_str)
                        users_msg = await users_msg.edit(content=msg_content)
        
        # Final results
        # TODO: go over this, see if it's really needed (it's not)
        try:
            ready_users.remove(self.bot.user.id)
        except:
            pass
        
        if len(ready_users) > 0:
            ready_embed = discord.Embed(title="Ready Users", description=" ".join(["<@{}>".format(str(uid)) for uid in ready_users]), color=discord.Colour.green())
            await ctx.send(embed=ready_embed)

        if len(waiting_users) > 0:
            afk_embed = discord.Embed(title="AFK Users", description=" ".join(["<@{}>".format(str(uid)) for uid in waiting_users]), color=discord.Colour.red())
            await ctx.send(embed=afk_embed)


# TODO: what if someone un-reacts to final ready check
