from typing import Literal

# TODO: clean up imports
import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.chat_formatting import inline, humanize_list, bold
from redbot.core.utils.embed import randomize_colour
import asyncio
import time
from datetime import datetime
from typing import Optional
import json

TOTAL_WC = "total_wc"
SPRINTS = "sprints"
AVG_WPM = "avg_wpm"

# users -> {uid: total wordcount}
defaults = {
    "users": {},
    "settings": {
        "join_wait_time": 180,
        "default_sprint_time": 1,
        "cutoff_wpm": 10 
    }
}


# TODO: make adjustable
TIME_TO_JOIN = 20 
DEFAULT_SPRINT_TIME = 1    # In minutes

# TODO: add function for removing user data

class Sprint(commands.Cog):
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

        # Sprint-specific variables
        self.ongoing = False
        self.sprint_msg = None
        self.current_sprint = {}
        self.sprint_cancelled = False

        # Set up settings
        self._time_to_join = None
        self._default_sprint_time = None
        self._cutoff_wpm = None

    async def _setup_settings(self, ctx):
        settings = await self.config.guild(ctx.guild).settings()
        self._time_to_join = settings['join_wait_time']
        self._default_sprint_time = settings['default_sprint_time']
        self._cutoff_wpm = settings['cutoff_wpm']

    async def _get_prefix(self, ctx):
        prefix = await self.bot.get_valid_prefixes(ctx.guild)
        return prefix[0]

    ##############################################
    #### Sprint-specific commands

    @commands.group()
    @commands.guild_only()
    async def sprint(self, ctx):
        """
            Command group for sprints
        """
    
    @sprint.command(aliases=["create"])
    async def start(self, ctx, sprint_time = None):
        """
            Start a new sprint
        """
        prefix = await self._get_prefix(ctx)

        if self.ongoing:
            await ctx.send("There's already an ongoing sprint! Enter " + inline("{}sprint join <word-count>".format(prefix)) + " to join the sprint!", reference=self.sprint_msg)
            return

        # TODO: turn into decorator
        if self._time_to_join is None:
            await self._setup_settings(ctx)

        # Sprint time checking
        if not sprint_time:
            sprint_time = DEFAULT_SPRINT_TIME
        else:
            try:
                sprint_time = int(sprint_time)
            except ValueError:
                msg = "Invalid sprint time! Enter " + inline("{}sprint start <number>".format(prefix)) + " for sprint. (Ex: " + inline("{}sprint start 30".format(prefix)) + " for a 30 minute sprint. (Or, type " + inline("{}sprint help".format(prefix)) + " for more info)"
                await ctx.send(msg)
                return

        self.ongoing = True
        self.current_sprint = {}

        time_to_wait = int(time.time() + TIME_TO_JOIN + 1)    # Extra second is time for the bot to send/delete message

        msg_content = "Sprint starting <t:{}:R>. Enter ".format(time_to_wait) + inline("{}sprint join <word-count>".format(prefix)) + " to join the sprint!"
        msg_embed = discord.Embed(title="🌟🌟🌟 SPRINT STARTING 🌟🌟🌟", description=msg_content)
        self.sprint_msg = await ctx.send(embed=msg_embed)
        await asyncio.sleep(TIME_TO_JOIN)


        if self.sprint_cancelled:
            self.sprint_cancelled = False
            return

        # Start sprint & notify
        await self.sprint_msg.delete()

        time_to_sprint = DEFAULT_SPRINT_TIME * 60
        sprint_timestamp = int(time.time() + time_to_sprint + 1)

        msg_content = "Sprint ends <t:{}:R> left! Go!!!! \n".format(sprint_timestamp)
        msg_embed = randomize_colour(discord.Embed(title="🌟🌟🌟 SPRINT STARTED 🌟🌟🌟", description=msg_content))
        self.sprint_msg = await ctx.send(embed=msg_embed)
        await ctx.send(humanize_list(["<@{}>".format(uid) for uid in self.current_sprint]))

        await asyncio.sleep(time_to_sprint)

        if self.sprint_cancelled:
            self.sprint_cancelled = False
            return

        # Finish sprint & notify
        await self.sprint_msg.delete()

        msg_content = "You have 3 minutes to enter your word count!"
        msg_embed = randomize_colour(discord.Embed(title="🌟🌟🌟 SPRINT ENDED 🌟🌟🌟", description=msg_content))
        await ctx.send(embed=msg_embed)

        await ctx.send(humanize_list(["<@{}>".format(uid) for uid in self.current_sprint]))
        await asyncio.sleep(3*60)

        final_wc = [[user, self.current_sprint[user][1]] for user in self.current_sprint.keys()]
        final_wc.sort(key=lambda x: x[1])

        msg_content = ""
        for i, record in enumerate(final_wc):
            msg_content = "{}. <@{}> — {} words ({} wpm) \n".format(i+1, record[0], record[1], record[1]//sprint_time)
        msg_embed = randomize_colour(discord.Embed(title="🌟🌟🌟 LEADERBOARD 🌟🌟🌟", description=msg_content))
        await ctx.send(embed=msg_embed)


        # Save per-user data
        ## TODO: change so wpm isn't calculated twice
        today = datetime.today().strftime('%Y-%m-%d')
        async with self.config.guild(ctx.guild).users() as users:
            for record in final_wc:
                wpm = record[1]//sprint_time
                uid = str(record[0])

                if wpm <= self._cutoff_wpm:
                    wpm = "?"

                try: 
                    user_info = users[uid]
                    user_info[TOTAL_WC] += record[1]

                    n_records = len(user_info[SPRINTS])
                    if wpm != "?":
                        user_info[AVG_WPM] = wpm * (1/(n_records + 1)) + user_info[AVG_WPM] * (n_records/(n_records + 1))

                    user_info[SPRINTS].append([today, record[1]])
                
                # If user doesn't exist, create record for them
                except KeyError:
                    users[uid] = {
                        TOTAL_WC: record[1],
                        AVG_WPM: wpm,
                        SPRINTS: [[today, record[1]]]
                    }


        warning_embed = discord.Embed(title="NOTICE", description="This writing bot is still under construction! If you have any tips or suggestions, feel free to let me know [link](https://google.com)!", color=discord.Colour.gold())
        await ctx.send(embed=warning_embed)


        # Clean up
        self.ongoing = False
        
        
    @sprint.command()
    async def join(self, ctx, word_count = 0):
        """
            Join the sprint! Wordcount optional.
        """
        if not self.ongoing:
            prefix = await self._get_prefix(ctx)
            await ctx.send("No sprints currently running! Type " + inline("{}sprint start".format(prefix)) + " to start one!")
            return

        try:
            word_count = int(word_count)
        except ValueError:
            await ctx.send("Invalid word count! Please enter a number.")
            return

        self.current_sprint[str(ctx.author.id)] = [word_count, word_count]
        await ctx.send("You have joined with {} words.".format(word_count), reference=ctx.message)


    @sprint.command(aliases=["word"])
    async def words(self, ctx, word_count = 0):
        """
            Update word count for a sprint
        """
        if not self.ongoing:
            prefix = await self._get_prefix(ctx)
            await ctx.send("No sprints currently running! Type " + inline("{}sprint start".format(prefix)) + " to start one!")
            return

        try:
            word_count = int(word_count)
        except ValueError:
            await ctx.send("Invalid word count! Please enter a number.")
            return
        #######
        uid = str(ctx.author.id)
        try:
            prev_wc = self.current_sprint[uid][1]
        except KeyError:
            prev_wc = 0
            self.current_sprint[uid] = [0, 0]

        await ctx.send("Word count updated: {} words ({} new)".format(word_count, word_count - prev_wc), reference=ctx.message)

        self.current_sprint[uid][1] = word_count


    @sprint.command()
    async def cancel(self, ctx):
        """
            Stop the sprint.
        """
        # Make it so people vote and if majority rules then yeah sprint cancelled
        self.ongoing = False
        self.sprint_cancelled = True
        await self.sprint_msg.delete()
        await ctx.send("Sprint has been cancelled!")


    #### Settings-specifc commands
    @sprint.command()
    async def listSettings(self, ctx):
        """
            List bot settings
        """
        if self._time_to_join is None:
            await self._setup_settings(ctx)
        
        msg = bold("Time to Join") + ": " + inline(str(self._time_to_join)) + "\n" + "Time to join a sprint (in seconds)" + "\n\n"
        msg += bold("Default Sprint Time") + ": " + inline(str(self._default_sprint_time)) + "\n" + "Default sprint time if not specified (in minutes)" + "\n\n"
        msg += bold("Cutoff WPM") + ": " + inline(str(self._cutoff_wpm)) + "\n" + "Cutoff wpm to not add to users' average WPM" + "\n\n"

        settings_embed = discord.Embed(title="Settings", description=msg, color=discord.Colour.blue())
        await ctx.send(embed=settings_embed)

    @sprint.command()
    async def getStats(self, ctx):
        """
            Get lifetime user stats.
        """
        users = await self.config.guild(ctx.guild).users()

        try: 
            user_info = users[str(ctx.author.id)]

            msg = bold("User") + ": " + "<@{}>".format(ctx.author.id) + "\n"
            msg += bold("Total Word Count") + ": " + str(user_info[TOTAL_WC]) + "\n"
            msg += bold("Average Words Per Minute") + ": " + str(round(user_info[AVG_WPM], 1)) + "\n"
            msg += bold("Number of Sprints") + ": " + str(len(user_info[SPRINTS]))

            user_info_embed = discord.Embed(title="User Stats", description=msg, color=discord.Colour.blue())
            await ctx.send(embed=user_info_embed)
        
        except KeyError:
            msg_embed = discord.Embed(title="User Stats", description="No info yet! Participate in a sprint to get started.", color=discord.Colour.blue())
            await ctx.send(embed=msg_embed)
    


    @sprint.command()
    async def deleteMe(self, ctx):
        """
            Delete all of your sprint info completely from the bot.
        """
        wait_time = 5*60
        timelimit = time.time() + wait_time
        await ctx.send("Are you sure you want to delete your data? This action cannot be reversed!")
        while time.time() < timelimit:
            msg = await self.bot.wait_for("message", check=MessagePredicate.same_context(ctx))
            msg_content = msg.content.strip().lower()
            if msg_content.strip().lower()[0] == 'y':
                uid = str(ctx.author.id)
                self._delete_info_for_user(ctx, uid)
            else:
                return


    @sprint.command()
    @checks.admin_or_permissions(ban_members=True)
    async def deleteForUID(self, ctx, uid:str):
        """
            Delete info for users with a specific UID.
        """
        self._delete_info_for_user(ctx, uid)


    async def _delete_info_for_user(self, ctx, uid):
        async with self.config.guild(ctx.guild).users() as users:
            try:
                del users[uid]
                await ctx.send("Info for <@{}> deleted!".format(uid))
            except KeyError:
                await ctx.send("There's no information on <@{}> to be deleted!".format(uid))

    @sprint.command()
    @checks.admin_or_permissions(ban_members=True)
    async def dumpUserData(self, ctx):
        """
            Dumps all sprint data for this guild into a JSON file. (For migration purposes)
        """
        async with self.config.guild(ctx.guild).users() as users:
            filepath = "user_data_{}.json".format(time.time())
            with open(filepath, 'w') as outfile:
                json.dump(users, outfile, indent=4)

                # Send file
                await ctx.send(file=discord.File(filepath, filepath))

    @sprint.command()
    async def help(self, ctx):
        """
            Show more detailed help
        """
        prefix = await self._get_prefix(ctx)

        msg = "- To start a sprint, enter " + inline("{}sprint start".format(prefix)) + f" to run a sprint for {self._default_sprint_time} minutes. For a sprint with another length, enter " + inline("{}sprint start <minutes>".format(prefix)) + "\nFor example, for a sprint that's 25 minutes long, enter: " + inline("{}sprint start 25".format(prefix)) + "\n"
        msg += "- After that, join the sprint using " + inline("{}sprint join".format(prefix)) + "\nIf you'd like to join with a specific word count, enter " + inline("{}sprint join <word count>".format(prefix)) + "\nFor example, for joining with 153 words, enter: " + inline("{}sprint join 153".format(prefix))  + "\n"
        msg += "- At any point during the sprint, you can update your word count with " + inline("{}sprint words <word count>".format(prefix)) + "\n"
        msg += "- To call off a sprint, enter " + inline("{}sprint cancel".format(prefix))
        msg += "\n\n"
        msg += "This cog is still under construction! If you've got any tips or suggestions or bug reports, feel free to let me know in the anonymous tip box [here](https://google.com)!"
        help_embed = discord.Embed(title="Help", description=msg, color=discord.Colour.gold())
        await ctx.send(embed=help_embed)