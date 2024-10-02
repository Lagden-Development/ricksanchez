import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from db import users


class RickBot_WatcherCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="optin", description="Opt-in to the watcher system")
    @app_commands.guild_only()
    async def _optin(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        query = users.find_one({"_id": user_id})

        if query is None:
            await interaction.followup.send("You are opted in by default.")

        elif query.get("watcher", True) is True:
            await interaction.followup.send("You are already opted in.")

        else:
            try:
                users.delete_one({"_id": user_id})
                await interaction.followup.send(
                    "You have opted in to the watcher system, it may take a few minutes to take effect."
                )
            except Exception as e:
                await interaction.followup.send(f"An error occurred: {str(e)}")

    @app_commands.command(name="optout", description="Opt-out of the watcher system")
    @app_commands.guild_only()
    async def _optout(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        query = users.find_one({"_id": user_id})

        if query is None:
            users.insert_one({"_id": user_id, "watcher": False})
            await interaction.followup.send("You have opted out of the watcher system.")

        elif query.get("watcher", True) is False:
            await interaction.followup.send("You are already opted out.")

        else:
            try:

                users.delete_one({"_id": user_id})
                users.insert_one({"_id": user_id, "watcher": False})
                await interaction.followup.send(
                    "You have opted out of the watcher system."
                )
            except Exception as e:
                await interaction.followup.send(f"An error occurred: {str(e)}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RickBot_WatcherCommands(bot))
