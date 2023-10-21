import discord
from typing import Optional

class CheckView(discord.ui.View):
    def __init__(
        self,
        author: Optional[discord.abc.User] = None,
        *,
        timeout: float = 60.0,
    ):
        if timeout is None:
            raise TypeError("This view should not be used as a persistent view.")
        super().__init__(timeout=timeout)

        self.message: Optional[discord.Message] = None
        self.interacted_users = []

    async def on_timeout(self):
        if self.message is None:
            # we can't do anything here if message is none
            return

        try:
            await self.message.edit(view=view)
        except discord.HTTPException:
            # message could no longer be there or we may not be able to edit it anymore
            pass


    @discord.ui.button(label="Ready", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.interacted_users.append(interaction.user.id)
        self.stop()
        # respond to the interaction so the user does not see "interaction failed".
        await interaction.response.defer()
        # call `on_timeout` explicitly here since it's not called when `stop()` is called.
        await self.on_timeout()
    