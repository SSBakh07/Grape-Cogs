from typing import Literal

# TODO: clean up imports
import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import inline
from redbot.core.utils.embed import randomize_colour
import re

TWT = "twt"
IG = "ig"

defaults = {
    "toggle": {
        TWT: True,
        IG: True
    }
}

class SMFixer(commands.Cog):
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

    async def _get_prefix(self, ctx):
        prefix = await self.bot.get_valid_prefixes(ctx.guild)
        return prefix[0]

    def find_occurrence_twt(self, msg):
        reg_str = "(https:\/\/)(twitter|x)(\.com\/)([a-zA-Z0-9_\/\?\=\&]+)"
        return re.findall(reg_str, msg)
    
    def find_occurrence_ig(self, msg):
        reg_str = "(https:\/\/)(instagram)(\.com\/)([a-zA-Z0-9_\/\?\=\&]+)"
        return re.findall(reg_str, msg)

    ##############################################
    
    @commands.group()
    async def smfixer(self, ctx):
        """
            Command group for sm fixer
        """

    @smfixer.command()
    async def help(self, ctx):
        """
            Help on how to use this cog
        """
        prefix = await self._get_prefix(ctx)
        msg = "- Toggle everything: " + inline("{}smfixer toggle".format(prefix)) + "\n"
        msg += "- Toggle Twitter fixing: " + inline("{}smfixer toggleTwt".format(prefix)) + "\n"
        msg += "- Toggle Instagram fixing: " + inline("{}smfixer toggleIg".format(prefix)) + "\n"
        msg_embed = randomize_colour(discord.Embed(title="smfixer Guide", description=msg))
        await ctx.send("To be implemented")

    @smfixer.command()
    async def toggle(self, ctx):
        """
            Toggle all social media embed fixing
        """
        toggle = await self.config.guild(ctx.guild).toggle()
        val = toggle[TWT] and toggle[IG]
        val = not val

        toggle[TWT] = val
        toggle[IG] = val

        await self.config.guild(ctx.guild).toggle.set(toggle)

        await ctx.send("Social media fixer set to: " + inline(str(val)))

    @smfixer.command()
    async def toggleTwt(self, ctx):
        """
            Toggle Twitter/X embed fixing
        """
        toggle = await self.config.guild(ctx.guild).toggle()
        toggle[TWT] = not toggle[TWT]
        
        await self.config.guild(ctx.guild).toggle.set(toggle)

        await ctx.send("Twitter fixer set to: " + inline(str(val)))
    

    @smfixer.command()
    async def toggleIg(self, ctx):
        """
            Toggle Instagram embed fixing
        """
        toggle = await self.config.guild(ctx.guild).toggle()
        toggle[IG] = not toggle[IG]
        
        await self.config.guild(ctx.guild).toggle.set(toggle)

        await ctx.send("Instagram fixer set to: " + inline(str(val)))
    

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        async with self.config.guild(ctx.guild).toggle() as toggle:
            if not toggle or message.author == self.bot.user.id:
                return
            
            msg_content = message.content

            twt_matches = self.find_occurrence_twt(msg_content)
            if len(twt_matches) > 0:
                for match in twt_matches:
                    _match = list(match)
                    _match[1] = "vxtwitter"
                    await message.channel.send(''.join(_match))
                return
            
            ig_matches = self.find_occurrence_ig(msg_content)
            if len(ig_matches) > 0:
                for match in ig_matches:
                    _match = list(match)
                    _match[1] = "instagramez"
                    await message.channel.send(''.join(_match))
                return