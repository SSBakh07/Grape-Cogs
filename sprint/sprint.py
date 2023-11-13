import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.chat_formatting import inline, humanize_list, bold, italics
from redbot.core.utils.embed import randomize_colour
import asyncio
import time
from datetime import datetime
# import json






TOTAL_WC = "total_wc"
SPRINTS = "sprints"
AVG_WPM = "avg_wpm"
LAST_WC = "last_wc"

SETTINGS_VARS = "settings"
USERS_VARS = "users"

SPRINT_MSG = "sprint_msg"
CURRENT_SPRINT = "current_sprint"
WAITING_FOR = "waiting_for"
SPRINT_ID_KEY = "sprint_id"

# User-specific sprint stats
START_WC = "start_wc"
END_WC = "end_wc"

## Settings
JOIN_WAIT_KEY = "join_wait_time"
SPRINT_TIME_KEY = "default_sprint_time"
CUTOFF_WPM_KEY = "cutoff_wpm"

defaults = {
    "guilds": {}
}

# Default settings to set for new guild
default_settings = {
    # JOIN_WAIT_KEY: 180,
    JOIN_WAIT_KEY: 30,
    SPRINT_TIME_KEY: 15,
    CUTOFF_WPM_KEY: 10 
}


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

        self.sprint_dict = {}


    async def _get_settings_for_guild(self, guild_id):
        guilds_data = await self.config.guild(ctx.guild).guilds()
        try:
            guild = guilds_data[str(guild_id)]
            return guild[SETTINGS_VARS]
        except KeyError:
            return -1
    
    async def _setup_default_guild(self, guild, ctx=None):
        guild_id = str(guild.id)



        async with self.config.guild(guild).guilds() as guilds:
            guilds[guild_id] = {
                USERS_VARS: {},
                SETTINGS_VARS: default_settings.copy()
            }

        self.sprint_dict[guild_id] = {
            SPRINT_MSG: -1,
            CURRENT_SPRINT: {},
            WAITING_FOR: [],
            SPRINT_ID_KEY: -1
        }

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

        # guilds = await self.config.guild(ctx.guild).guilds()
        guild_id = str(ctx.guild.id)

        guild = None

        guilds = await self.config.guild(ctx.guild).guilds()

        try:
            guild = guilds[guild_id]
        except KeyError:
            guild = {
                USERS_VARS: {},
                SETTINGS_VARS: default_settings.copy()
            }

            guilds[guild_id] = guild
            await self.config.guild(ctx.guild).guilds.set(guilds)     

        self.sprint_dict[guild_id] = {
            SPRINT_MSG: -1,
            CURRENT_SPRINT: {},
            WAITING_FOR: [],
            SPRINT_ID_KEY: -1
        }       


            
        if self.sprint_dict[guild_id][SPRINT_ID_KEY] != -1:
            await ctx.send("There's already an ongoing sprint! Enter " + inline("{}sprint join <word-count>".format(prefix)) + " to join the sprint! (Omit " + inline("<word-count>") + " to start from 0 words)", reference=self.sprint_dict[guild_id][SPRINT_MSG])
            return
            
        # Sprint time checking
        if not sprint_time:
            sprint_time = guild[SETTINGS_VARS][SPRINT_TIME_KEY]
        else:
            try:
                sprint_time = int(sprint_time)
            except ValueError:
                msg = "Invalid sprint time! Enter " + inline("{}sprint start <number>".format(prefix)) + " for sprint. (Ex: " + inline("{}sprint start 30".format(prefix)) + " for a 30 minute sprint. (Or, type " + inline("{}sprint help".format(prefix)) + " for more info)"
                await ctx.send(msg)
                return
        
        self.sprint_dict[guild_id][CURRENT_SPRINT] = {}

        sprint_id = str(int(time.time()))
        self.sprint_dict[guild_id][SPRINT_ID_KEY] = sprint_id

        # time_to_wait = int(time.time() + guild[SETTINGS_VARS][JOIN_WAIT_KEY] + 1)    # Extra second is time for the bot to send/delete message        
        time_to_wait = int(time.time() + 30 + 1)

        msg_content = "Sprint starting <t:{}:R> for {} minutes. Enter ".format(time_to_wait, sprint_time) + inline("{}sprint join <word-count>".format(prefix)) + " to join the sprint! (Omit " + inline("<word-count>") + " to start with 0 words)"
        msg_embed = randomize_colour(discord.Embed(title="🌟🌟🌟 SPRINT STARTING 🌟🌟🌟", description=msg_content))

        self.sprint_dict[guild_id][SPRINT_MSG] = await ctx.send(embed=msg_embed)

        await asyncio.sleep(guild[SETTINGS_VARS][JOIN_WAIT_KEY])


        # If sprint was cancelled during this time
        if self.sprint_dict[guild_id][SPRINT_ID_KEY] != sprint_id:
            return

        # Start sprint & notify
        await self.sprint_dict[guild_id][SPRINT_MSG].delete()

    
        if len(self.sprint_dict[guild_id][CURRENT_SPRINT]) == 0:
            await ctx.send("No one joined the sprint! Stopping :(")
            self.sprint_dict[guild_id][SPRINT_ID_KEY] = -1
            return


        time_to_sprint = sprint_time * 60
        sprint_timestamp = int(time.time() + time_to_sprint + 1)

        msg_content = "Sprint ends <t:{}:R> left! Go!!!! \n".format(sprint_timestamp)
        msg_embed = randomize_colour(discord.Embed(title="🌟🌟🌟 SPRINT STARTED 🌟🌟🌟", description=msg_content))
        self.sprint_dict[guild_id][SPRINT_MSG] = await ctx.send(embed=msg_embed)


        await ctx.send(humanize_list(["<@{}>".format(uid) for uid in self.sprint_dict[guild_id][CURRENT_SPRINT]]))

        await asyncio.sleep(time_to_sprint)

        if self.sprint_dict[guild_id][SPRINT_ID_KEY] != sprint_id:
            return

        # Finish sprint & notify
        await self.sprint_dict[guild_id][SPRINT_MSG].delete()
        self.sprint_dict[guild_id][WAITING_FOR] = [uid for uid in self.sprint_dict[guild_id][CURRENT_SPRINT].keys()]

        msg_content = "You have 3 minutes to enter your word count! Enter " + inline("{}sprint words <word-count>".format(prefix)) + " to enter your final word count!"
        msg_embed = randomize_colour(discord.Embed(title="🌟🌟🌟 SPRINT ENDED 🌟🌟🌟", description=msg_content))
        await ctx.send(embed=msg_embed)


        await ctx.send(humanize_list(["<@{}>".format(uid) for uid in self.sprint_dict[guild_id][CURRENT_SPRINT].keys()]))

        turnin_timeout = time.time() + 3*60
        while len(self.sprint_dict[guild_id][WAITING_FOR]) > 0 and time.time() < turnin_timeout:
            await asyncio.sleep(1)

            
        # Calculate final wordcount for everyone.
        final_wc = []
        for user in self.sprint_dict[guild_id][CURRENT_SPRINT].keys():
            user_dict = self.sprint_dict[guild_id][CURRENT_SPRINT][user]
            wc_diff = user_dict[END_WC] - user_dict[START_WC]
            wpm = wc_diff/sprint_time

            final_wc.append([user, wc_diff, wpm])
        final_wc.sort(key=lambda x: x[2])


        # Send leaderboard
        msg_content = ""
        for i, result in enumerate(final_wc):
            user, wc_diff, wpm = result
            msg_content = "{}. <@{}> — {} words ({} wpm) \n".format(i+1, user, wc_diff, wpm)
            
        msg_content += "\n\n" + italics("(Note that wpms under {} aren't counted towards average WPM)".format(guild[SETTINGS_VARS][CUTOFF_WPM_KEY]))
        msg_embed = randomize_colour(discord.Embed(title="🌟🌟🌟 LEADERBOARD 🌟🌟🌟", description=msg_content))
        await ctx.send(embed=msg_embed)


        # theres a bug: https://discord.com/channels/1065798475524079826/1145395914207408138/1172898163900829696



        today = datetime.today().strftime('%Y-%m-%d')

        for uid, words, wpm in final_wc:
            if wpm <= guild[SETTINGS_VARS][CUTOFF_WPM_KEY]:
                wpm = "?"

            try: 
                user_info = guild[USERS_VARS][uid]
                user_info[TOTAL_WC] += words

                n_records = len(user_info[SPRINTS])
                if wpm != "?":
                    user_info[AVG_WPM] = wpm * (1/(n_records + 1)) + user_info[AVG_WPM] * (n_records/(n_records + 1))

                user_info[SPRINTS].append([today, words])
                user_info[LAST_WC] = self.sprint_dict[guild_id][CURRENT_SPRINT][uid][END_WC]
            
            # If user doesn't exist, create record for them
            except KeyError:
                guild[USERS_VARS][uid] = {
                    TOTAL_WC: words,
                    AVG_WPM: wpm,
                    SPRINTS: [[today, words]],
                    LAST_WC: self.sprint_dict[guild_id][CURRENT_SPRINT][uid][END_WC]
                }

        await self.config.guild(ctx.guild).guilds.set(guilds)  


        warning_embed = discord.Embed(title="NOTICE", description="This writing bot is still under construction! If you have any tips or suggestions, feel free to let me know [here](https://forms.gle/Whh2d5zDNkWtDQ876)!", color=discord.Colour.gold())
        await ctx.send(embed=warning_embed)


        # Clean up
        self.sprint_dict[guild_id][SPRINT_ID_KEY] = -1
            
        
        
    @sprint.command()
    async def join(self, ctx, word_count = "0"):
        """
            Join the sprint! Wordcount optional.
        """
        guild_id = str(ctx.guild.id)

        if self.sprint_dict[guild_id][SPRINT_ID_KEY] == -1:
            prefix = await self._get_prefix(ctx)
            await ctx.send("No sprints currently running! Type " + inline("{}sprint start".format(prefix)) + " to start one!")
            return

        try:
            if "same" in word_count.lower():
                guilds = await self.config.guild(ctx.guild).guilds()
                try:
                    users = guilds[guild_id][USERS_VARS]
                    word_count = users[str(ctx.author.id)][LAST_WC]
                except KeyError:
                    await ctx.send("No user data yet! Finish a sprint to get started.")
                    return
            else:
                word_count = int(word_count)
        except ValueError:
            await ctx.send("Invalid word count! Please enter a number.")
            return


        # self.sprint_dict[guild_id][CURRENT_SPRINT][str(ctx.author.id)] = [word_count, word_count]
        self.sprint_dict[guild_id][CURRENT_SPRINT][str(ctx.author.id)] = {
            START_WC: word_count,
            END_WC: word_count
        }
        await ctx.send("You have joined with {} words.".format(word_count), reference=ctx.message)


    @sprint.command(aliases=["word"])
    async def words(self, ctx, word_count):
        """
            Update word count for a sprint
        """
        guild_id = str(ctx.guild.id)

        if self.sprint_dict[guild_id][SPRINT_ID_KEY] == -1:
            prefix = await self._get_prefix(ctx)
            await ctx.send("No sprints currently running! Type " + inline("{}sprint start".format(prefix)) + " to start one!")
            return

        try:
            word_count = int(word_count)
        except ValueError:
            await ctx.send("Invalid word count! Please enter a number.")
            return


        uid = str(ctx.author.id)
        try:
            prev_wc = self.sprint_dict[guild_id][CURRENT_SPRINT][uid][END_WC]
        except KeyError:
            prev_wc = 0
            self.sprint_dict[guild_id][CURRENT_SPRINT][uid][START_WC] = 0
            self.sprint_dict[guild_id][CURRENT_SPRINT][uid][END_WC] = 0

        await ctx.send("Word count updated: {} words ({} new)".format(word_count, word_count - prev_wc), reference=ctx.message)

        self.sprint_dict[guild_id][CURRENT_SPRINT][uid][END_WC] = word_count

        try:
            self.sprint_dict[guild_id][WAITING_FOR].remove(uid)
        except ValueError:
            pass


    @sprint.command(aliases=["stop"])
    async def cancel(self, ctx):
        """
            Stop the sprint.
        """

        guild_id = str(ctx.guild.id)

        sprint_key = -1
        try:
            sprint_key = self.sprint_dict[guild_id][SPRINT_ID_KEY]
        except KeyError:
            pass

        if sprint_key == -1:
            await ctx.send("There isn't a sprint running right now!")
            return

        # TODO: Make it so people vote and if majority rules then sprint cancelled rather than 1 person doing it
        self.sprint_dict[guild_id][SPRINT_ID_KEY] = -1
        await self.sprint_dict[guild_id][SPRINT_MSG].delete()
        self.sprint_dict[guild_id][SPRINT_MSG] = None

        cancel_embed = discord.Embed(title="SPRINT CANCELLED", description="The sprint has been called off!", color=discord.Colour.red())
        await ctx.send(embed=cancel_embed)


    #### Settings-specifc commands
    @sprint.command()
    async def listSettings(self, ctx):
        """
            List bot settings
        """

        # TODO: wrap this bit up in it's own little function that returns guild_id, guild (obj). this and start sprint and list user stats 
        async with self.config.guild(ctx.guild).guilds() as guilds:
            guild_id = str(ctx.guild.id)

            guild = None
            try:
                guild = guilds[guild_id]
            except KeyError:
                await self._setup_default_guild(ctx.guild)
                guild = guilds[guild_id]
            
            guild_settings = guild[SETTINGS_VARS]
        
            msg = bold("Time to Join") + ": " + inline(str(guild_settings[JOIN_WAIT_KEY])) + "\n" + "Time to join a sprint (in seconds)" + "\n\n"
            msg += bold("Default Sprint Time") + ": " + inline(guild_settings[SPRINT_TIME_KEY]) + "\n" + "Default sprint time if not specified (in minutes)" + "\n\n"
            msg += bold("Cutoff WPM") + ": " + inline(str(guild_settings[CUTOFF_WPM_KEY])) + "\n" + "Cutoff wpm to not add to users' average WPM" + "\n\n"

            settings_embed = discord.Embed(title="Settings", description=msg, color=discord.Colour.blue())
            await ctx.send(embed=settings_embed)


    # TODO: clean up
    @sprint.command()
    async def getStats(self, ctx):
        """
            Get lifetime user stats.
        """
        # users = await self.config.guild(ctx.guild).users()
        guilds = await self.config.guild(ctx.guild).guilds()

        guild_id = str(ctx.guild.id)

        guild = None
        try:
            guild = guilds[guild_id]
        except KeyError:
            await self._setup_default_guild(ctx.guild)
            guild = guilds[guild_id]

            msg_embed = discord.Embed(title="User Stats", description="No info yet! Participate in a sprint to get started.", color=discord.Colour.blue())
            await ctx.send(embed=msg_embed)
            return

        try: 
            # user_info = users[]
            uid = str(ctx.author.id)
            user_info = guild[USERS_VARS][uid]

            msg = bold("User") + ": " + "<@{}>".format(uid) + "\n"
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
        await ctx.send("This is a bit buggy - @ one of the admins to do this for you until I fix this.")
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
        await self._delete_info_for_user(ctx, uid)


    async def _delete_info_for_user(self, ctx, uid):
        # async with self.config.guild(ctx.guild).users() as users:
        async with self.config.guild(ctx.guild).guilds() as guilds:
            guild_id = str(ctx.guild.id)

            guild = None
            try:
                guild = guilds[guild_id]
            except KeyError:
                await self._setup_default_guild(ctx.guild)
                await ctx.send("There's no information on <@{}> to be deleted!".format(uid))
                return 

            try:
                del guild[USERS_VARS][uid]
                await ctx.send("Info for <@{}> deleted!".format(uid))
            except KeyError:
                await ctx.send("There's no information on <@{}> to be deleted!".format(uid))


    # @sprint.command()
    # @checks.admin_or_permissions(ban_members=True)
    # async def dumpUserData(self, ctx):
    #     """
    #         Dumps all sprint data for this guild into a JSON file. (For migration purposes)
    #     """
    #     async with self.config.guild(ctx.guild).users() as users:
    #         filepath = "user_data_{}.json".format(time.time())
    #         with open(filepath, 'w') as outfile:
    #             json.dumps(users, outfile, indent=4)

    #             # Send file
    #             await ctx.send(file=discord.File(filepath, filepath))

    @sprint.command()
    async def help(self, ctx):
        """
            Show more detailed help
        """

        guild_id = str(ctx.guild.id)
        guild = None


        for i in range(3):
            guilds = await self.config.guild(ctx.guild).guilds()
            try:
                guild = guilds[guild_id]
            except KeyError:
                await self._setup_default_guild(ctx.guild)
            # guild = guilds[guild_id]


        prefix = await self._get_prefix(ctx)
        guild_settings = guild[SETTINGS_VARS]

        msg = "- To start a sprint, enter " + inline("{}sprint start".format(prefix)) + f" to run a sprint for {guild_settings[SPRINT_TIME_KEY]} minutes. For a sprint with another length, enter " + inline("{}sprint start <minutes>".format(prefix)) + "\nFor example, for a sprint that's 25 minutes long, enter: " + inline("{}sprint start 25".format(prefix)) + "\n"
        msg += "- After that, join the sprint using " + inline("{}sprint join".format(prefix)) + "\nIf you'd like to join with a specific word count, enter " + inline("{}sprint join <word count>".format(prefix)) + "\nFor example, for joining with 153 words, enter: " + inline("{}sprint join 153".format(prefix))  + "\nYou can also join with the word count at the end of your last sprint using: " + inline("{}sprint join same".format(prefix)) + "\n"
        msg += "- At any point during the sprint, you can update your word count with " + inline("{}sprint words <word count>".format(prefix)) + "\n"
        msg += "- To call off a sprint, enter " + inline("{}sprint cancel".format(prefix))
        msg += "\n\n"
        msg += "This cog is still under construction! If you've got any tips or suggestions or bug reports, feel free to let me know in the anonymous tip box [here](https://forms.gle/Whh2d5zDNkWtDQ876)!"
        help_embed = discord.Embed(title="Help", description=msg, color=discord.Colour.gold())
        await ctx.send(embed=help_embed)


    @sprint.command()
    @checks.admin_or_permissions(ban_members=True)
    async def wipeAllData(self, ctx):
        """
            Wipes all data for all users in a guild
        """
        
        await self._setup_default_guild(ctx.guild)
        await ctx.send("All data for all users of this server has been deleted.")

    @sprint.command()
    @checks.admin_or_permissions(ban_members=True)
    async def get_sprint_id(self, ctx):
        try:
            await ctx.send(str(self.sprint_dict[str(ctx.guild.id)][SPRINT_ID_KEY]))
        except:
            await ctx.send("No id yet")

    @sprint.command()
    @checks.admin_or_permissions(ban_members=True)
    async def get_sprint_dict(self, ctx):
        await ctx.send(str(self.sprint_dict))