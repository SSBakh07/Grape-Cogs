from typing import Literal

# TODO: clean up imports
import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import inline, italics
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.embed import randomize_colour
from redbot.core.utils.predicates import MessagePredicate
import re

# {"username":__, "reason": ___}

TOGGLE = "toggle"
LOG_CHANNEL = "log_channel"
BLOCKED = "blocked"
ACTION_LEVEL = "action_level"

defaults = {
    TOGGLE: True,
    BLOCKED: [],
    LOG_CHANNEL: None,
    ACTION_LEVEL: 0
}

al_desc = {
    "0": "Log only (log channel must be set)",
    "1": "Notify user in DMs",
    "2": "Delete message",
    "3": "Timeout user (NOT IMPLEMENTED)",
    "4": "Kick user (NOT IMPLEMENTED)"
}

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

    ### Utility functions

    def find_occurrence_twt(self, msg):
        reg_str = "(https:\/\/)(twitter|x)(\.com\/)([a-zA-Z0-9_\/\?\=\&]+)"
        return re.findall(reg_str, msg)

    def construct_warning_embed(self, guild_name, url, reason, message_url=None, action_level=0):
        msg_action = "flagged"
        if action_level > 1:
            msg_action = "deleted"

        msg = f"# Message Blocked \n### **Your message in {guild_name} has been {msg_action} because it contained a tweet sent by a user blacklisted in the server.** \n"
        msg += f"**__Tweet__:** {url} \n"
        if action_level < 2:
            msg += "**__Message__**: " + message_url + "\n"
        msg += f"**__Reason__:** " + inline("{}".format(reason)) + "\n"
        msg += f"\n*If you think this has been a mistake, feel free to reach out!*"

        return discord.Embed(description=msg, color=discord.Colour.orange())
    
    def construct_log_msg(self, blocked_user, author_id, twt_url, msg_url):
        # msg += f"# Blocked Twitter URL\n"
        msg = ""
        msg += "**__Blocked Twitter User__**: " + inline(blocked_user) + "\n"
        msg += "**__Tweet__**: " + inline(twt_url) + "\n"
        msg += f"**__User__**: <@{author_id}>" + "\n"
        msg += f"**__Message__**: {msg_url}"

        
        return discord.Embed(title="Blocked Message", description=msg, color=discord.Colour.yellow())
    
    def fix_username(self, username):
        return username.strip().lower().replace("@", "")

    async def _get_prefix(self, ctx):
        prefix = await self.bot.get_valid_prefixes(ctx.guild)
        return prefix[0]

    ##############################################

    @checks.admin_or_permissions(ban_members=True)
    @commands.group(aliases=["tf"])
    async def twtfilter(self, ctx):
        """
            Command group for twitter filter
        """


    @twtfilter.command()
    async def help(self, ctx):
        """
            Help on how to use this cog
        """
        prefix = await self._get_prefix(ctx)

        msg = ""
        msg += "- " + inline("create") + ": Create a new filter\n"
        msg += italics("For example, enter ") + inline(f"{prefix}twitterfilter create elonmusk") + " " + italics("to create a new filter to block all tweets from the user @elonmusk. Additionally, you can enter a tweet url instead of a username.") + "\n\n"

        msg += "- " + inline("list") + ": List all existing filters\n\n"

        msg += "- " + inline("delete") + ": Delete an existing filter\n"
        msg += italics("For example, enter ") + inline(f"{prefix}twitterfilter delete ExampleUsername") + " " +  italics("to delete any filters existing for tweets from users with that specific username.") + "\n\n"

        msg += "- " + inline("setActionLevel") + ": Set Twitter filter action level\n"
        msg += italics("For example, enter ") + inline(f"{prefix}twitterfilter setActionLevel 1") + " " + italics("to set action level to 1. To learn more, enter ") + inline(f"{prefix}twitterfilter setActionLevel") + "\n\n"

        msg += "- " + inline("setLogChannel") + ": Set channel for log messages to be sent to\n"
        msg += italics("For example, enter ") + inline(f"{prefix}twitterfilter setLogChannel #mod-logs") + " " + italics("to send messages to a channel named #mod-logs in the server.") + "\n\n"
        msg += "- " + inline("toggle") + ": Toggle filter and embed functionality\n\n"

        msg += "- " + inline("toggle") + ": Toggle filter and embed functionality\n\n"

        msg += "- " + inline("listSettings") + ": List settings that have been set in the server\n\n"

        embed = discord.Embed(title="Twitter Filter Guide", description=msg, color=discord.Colour.green())
        await ctx.send(embed=embed)


    @twtfilter.command(aliases=["setlogchannel", "setLog", "setlog"])
    async def setLogChannel(self, ctx, channel: discord.TextChannel):
        """
            Set channel for log messages to be sent to.
        """
        await self.config.guild(ctx.guild).log_channel.set(channel.id)
        await ctx.send(f"Alerts will now be sent to <#{channel.id}>")
    

    @twtfilter.command()
    async def toggle(self, ctx):
        """
            Toggle filter and embed functionality
        """
        toggle = await self.config.guild(ctx.guild).toggle()
        toggle = not toggle
        await self.config.guild(ctx.guild).toggle.set(toggle)
        if toggle:
            await ctx.send("TwtFilter is now active.")
        else:
            await ctx.send("TwtFilter has been deactivated")


    @twtfilter.command(aliases=["setactionlevel", "setlevel", "setLevel"])
    async def setActionLevel(self, ctx, action_level):
        """
            Set Twitter filter action level
        """
        try:
            action_level = int(action_level)
            if action_level > 4:
                raise ValueError("InternalBotError: Invalid action value")
            await self.config.guild(ctx.guild).action_level.set(action_level)
            msg = "Action value set to: " + inline(str(action_level)) + "\n*(" + al_desc[str(action_level)] + ")*"
            await ctx.send(msg)

        except ValueError:
            msg = "**Invalid action value**\n"
            msg += "Possible values:\n"
            msg += inline("0") + ": " + al_desc["0"] + "\n"
            msg += inline("1") + ": " + al_desc["1"] + "\n"
            msg += inline("2") + ": " + al_desc["2"] + "\n"
            msg += inline("3") + ": " + al_desc["3"] + "\n"
            msg += inline ("4") + ": " + al_desc["4"] + "\n"
            await ctx.send(msg)


    @twtfilter.command(aliases=["createfilter", "create"])
    async def createFilter(self, ctx, user: str):
        """
            Create a new filter
        """
        # Just in case the user enters xitter url instead of raw username
        url_matches = self.find_occurrence_twt(user)
        if len(url_matches) > 0:
            user = url_matches[0][-1].split('/')[0].lower()
        else:
            user = self.fix_username(user)

        await ctx.send("**Creating filter for user: **" + inline(user))
        await ctx.send("Please enter why this user is being blocked. \n*(Warning: if DM warnings are on, the members of this server will see this)*")


        res_msg = await self.bot.wait_for("message", check=MessagePredicate.same_context(ctx))
        response = res_msg.content

        msg = "**User Blocked**: " + inline(user) + "\n"
        msg += "**Reason**: " + inline(response)
        msg_embed = discord.Embed(description=msg, title="Preview", color=discord.Colour.yellow())

        await ctx.send(embed=msg_embed)
        await ctx.send("Is this okay? (Enter " + inline("yes") + " to create filter)")

        msg = await self.bot.wait_for("message", check=MessagePredicate.same_context(ctx))

        msg_content = msg.content.lower().strip()
        if msg_content == 'yes':
            filters = await self.config.guild(ctx.guild).blocked()
            blocked_users = [f["username"] for f in filters]
            if user in blocked_users:
                await ctx.send("This user is already filtered! Stopping...")
            else:
                new_filter = {
                    "username": user,
                    "reason": response
                }
                filters.append(new_filter)
                await self.config.guild(ctx.guild).blocked.set(filters)
                await ctx.send("Filter created!")
        else:
            await ctx.send("Filter creation canceled.")

    @twtfilter.command(aliases=["listfilters", "listFilter", "listfilter", "list"])
    async def listFilters(self, ctx):
        """
            List all existing filters
        """
        filters = await self.config.guild(ctx.guild).blocked()
        if len(filters) > 0:
            embeds = []
            for filter in filters:
                msg = "**__User__**: " + inline(filter["username"]) + "\n"
                msg += "**__Reason__**: " + inline(filter["reason"])
                embeds.append(discord.Embed(description = msg, color=discord.Colour.orange()))
            await menu(ctx, embeds, DEFAULT_CONTROLS)
            return
        await ctx.send("There aren't any twitter filters yet.")
    

    @twtfilter.command(aliases=["deletefilter", "delete"])
    async def deleteFilter(self, ctx, username: str):
        """
            Delete an existing filter by username
        """
        username = self.fix_username(username)
        filters = await self.config.guild(ctx.guild).blocked()
        del_filter = [filter for filter in filters if filter["username"] == username]
        if len(del_filter) == 0:
            await ctx.send("There aren't any filters for this user.")
            return

        # Remove filter
        for f in del_filter:
            filters.remove(f)

        await self.config.guild(ctx.guild).blocked.set(filters)
        await ctx.send("Filter for user " + inline(username) + " deleted.")

    @twtfilter.command(aliases=["listsettings", "settings"])
    async def listSettings(self, ctx):
        """
            List settings for server
        """
        action_level = await self.config.guild(ctx.guild).action_level()
        action_level = str(action_level)

        toggle = await self.config.guild(ctx.guild).toggle()
        log_channel_id = await self.config.guild(ctx.guild).log_channel()

        msg = ""
        msg += f"- Is it on: " + inline(str(toggle)) + "\n"
        msg += f"- LogChannel: <#{log_channel_id}> \n"
        msg += f"- Action Level: " + inline(action_level) + " (" + italics(al_desc[action_level]) + ")" + "\n"

        embed = discord.Embed(title="Twitter Filter Settings", description=msg, color=discord.Colour.blue())
        await ctx.send(embed=embed)

        

    ##### Listeners

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        toggle = await self.config.guild(message.guild).toggle()

        if toggle:
            twt_matches = self.find_occurrence_twt(message.content)

            if len(twt_matches) > 0:
                blocked = await self.config.guild(message.guild).blocked()
                blocked_users = [b["username"] for b in blocked]

                for match in twt_matches:
                    url_params = match[-1]
                    username = url_params.split('/')[0].lower()
                    
                    try:
                        idx = blocked_users.index(username)
                        action_level = await self.config.guild(message.guild).action_level()

                        # Send warning message in guild
                        if action_level != 0:
                            
                            if action_level == 1:
                                warning_embed = self.construct_warning_embed(message.guild.name, ''.join(match), blocked[idx]["reason"], message_url=message.jump_url)

                            else:
                                await message.channel.send(f"guild name: {message.guild.name}")
                                await message.channel.send(f"reason: {blocked[idx]['reason']}")
                                warning_embed = self.construct_warning_embed(message.jump_url, ''.join(match), blocked[idx]["reason"], action_level=action_level)

                                # Delete message here
                                if action_level > 1:
                                    try: 
                                        await message.delete()
                                    except:
                                        pass

                            await message.author.send(embed=warning_embed)


                        # Send log message here
                        log_channel_id = await self.config.guild(message.guild).log_channel()
                        if log_channel_id:
                            log_channel = message.guild.get_channel(log_channel_id)

                            log_msg = self.construct_log_msg(username, message.author.id, ''.join(match), message.jump_url)
                            await log_channel.send(embed=log_msg)
                        

                    # If username is not blocked
                    except ValueError:
                        # pass
                        _match = list(match)
                        _match[1] = "vxtwitter"
                        await message.channel.send(''.join(_match))
