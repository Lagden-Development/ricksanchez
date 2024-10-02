import datetime, json
import discord
from discord.ext import (
    commands,
)
from typing import NoReturn, Dict, Any, Union
from db import (
    users,
)


def rgb_to_hex(
    rgb: tuple,
) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        rgb[0],
        rgb[1],
        rgb[2],
    )


def convert_discord_activity_type(
    activity: discord.Activity,
) -> str:
    activity_types = {
        discord.Game: "Game",
        discord.Streaming: "Streaming",
        discord.Activity: "Activity",
        discord.CustomActivity: "CustomActivity",
        discord.Spotify: "Spotify",
    }
    return activity_types.get(
        type(activity),
        "Unknown",
    )


class RickBot_Watcher(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
    ):
        self.bot = bot

    async def process_user_if_opted_in(self, user: Union[discord.Member, discord.User]):
        if user.bot:
            return

        query = users.find_one({"_id": user.id})
        if query is None or query.get("watcher", True):
            await self.process_user_data(user)
            if isinstance(user, discord.Member):
                await self.process_member_presence(user)

    async def evaluate_active_platforms(
        self,
        member: discord.Member,
    ) -> Dict[
        str,
        bool,
    ]:
        active_platforms = {
            "desktop": (
                True if member.desktop_status != discord.Status.offline else False
            ),
            "mobile": (
                True if member.mobile_status != discord.Status.offline else False
            ),
            "web": (True if member.web_status != discord.Status.offline else False),
        }
        return active_platforms

    def process_misc_activity(
        self,
        activity: discord.Activity,
    ) -> Dict[
        str,
        Any,
    ]:
        activity_data = {
            "name": activity.name,
            "type": convert_discord_activity_type(activity),
            "details": getattr(
                activity,
                "details",
                None,
            ),
            "state": getattr(
                activity,
                "state",
                None,
            ),
            "application_id": getattr(
                activity,
                "application_id",
                None,
            ),
            "created_at": (
                activity.created_at.isoformat() if activity.created_at else None
            ),
        }

        if hasattr(
            activity,
            "timestamps",
        ):
            activity_data["timestamps"] = {
                "start": activity.timestamps.get("start"),
                "end": activity.timestamps.get("end"),
            }

        activity_data["assets"] = {
            "large_image": getattr(
                activity,
                "large_image_url",
                None,
            ),
            "large_text": getattr(
                activity,
                "large_image_text",
                None,
            ),
            "small_image": getattr(
                activity,
                "small_image_url",
                None,
            ),
            "small_text": getattr(
                activity,
                "small_image_text",
                None,
            ),
        }

        return activity_data

    async def process_user_data(
        self,
        user: Union[discord.Member, discord.User],
    ):
        if user.bot:
            return

        if user.accent_color:
            accent_color = user.accent_color.to_rgb()
            accent_color = {
                "r": accent_color[0],
                "g": accent_color[1],
                "b": accent_color[2],
                "hex": rgb_to_hex(accent_color),
            }
        else:
            accent_color = None

        if user.color:
            color = user.color.to_rgb()
            color = {
                "r": color[0],
                "g": color[1],
                "b": color[2],
                "hex": rgb_to_hex(color),
            }
        else:
            color = None

        user_data = {
            "accent_color": accent_color,
            "accent_colour": accent_color,
            "avatar": (
                {
                    "key": str(user.avatar.key),
                    "url": str(user.avatar.url),
                }
                if user.avatar
                else None
            ),
            "avatar_decoration": str(user.avatar_decoration),
            "avatar_decoration_sku_id": user.avatar_decoration_sku_id,
            "banner": (
                {
                    "key": str(user.banner.key),
                    "url": str(user.banner.url),
                }
                if user.banner
                else None
            ),
            "color": color,
            "colour": color,
            "created_at": user.created_at.isoformat(),
            "discriminator": user.discriminator,
            "display_avatar": str(user.display_avatar),
            "display_name": user.display_name,
            "global_name": user.global_name,
            "id": user.id,
            "mention": user.mention,
            "name": user.name,
            "public_flags": user.public_flags.value,
        }

        try:
            result = users.update_one(
                {"_id": user.id},
                {"$set": {"user_data": user_data}},
                upsert=True,
            )

            if result.upserted_id:
                print(f"New user {user} added to the database.")
            else:
                print(f"User {user}'s data updated in the database.")
        except Exception as e:
            print(f"Error updating user {user} in the database: {str(e)}")

    async def process_member_presence(
        self,
        member: discord.Member,
    ):
        if member.bot:
            return

        user_statuses = {
            "desktop": str(member.desktop_status),
            "mobile": str(member.mobile_status),
            "web": str(member.web_status),
            "status": str(member.status),
            "raw_status": str(member.raw_status),
        }
        user_active_platforms = await self.evaluate_active_platforms(member)

        custom_status = None
        spotify_status = None
        misc_activities = []

        for activity in member.activities:
            if isinstance(
                activity,
                discord.CustomActivity,
            ):
                custom_status = {
                    "name": activity.name,
                    "emoji": (str(activity.emoji) if activity.emoji else None),
                    "state": activity.state,
                    "created_at": (
                        activity.created_at.isoformat() if activity.created_at else None
                    ),
                }
            elif isinstance(
                activity,
                discord.Spotify,
            ):
                activity_color = activity.color.to_rgb()
                spotify_status = {
                    "album": {
                        "name": activity.album,
                        "cover_url": activity.album_cover_url,
                    },
                    "track": {
                        "name": activity.title,
                        "url": activity.track_url,
                        "artists": activity.artists,
                        "start": (
                            activity.start.isoformat() if activity.start else None
                        ),
                        "end": (activity.end.isoformat() if activity.end else None),
                    },
                    "activity": {
                        "color": {
                            "r": activity_color[0],
                            "g": activity_color[1],
                            "b": activity_color[2],
                            "hex": rgb_to_hex(activity_color),
                        },
                        "created_at": (
                            activity.created_at.isoformat()
                            if activity.created_at
                            else None
                        ),
                        "type": convert_discord_activity_type(activity),
                        "title": activity.title,
                        "party_id": activity.party_id,
                    },
                }
            else:
                misc_activities.append(self.process_misc_activity(activity))

        try:
            update_data = {
                "presence_data": {
                    "statuses": user_statuses,
                    "active_platforms": user_active_platforms,
                    "custom_status": custom_status,
                    "spotify_status": spotify_status,
                    "misc_activities": misc_activities,
                }
            }

            result = users.update_one(
                {"_id": member.id},
                {"$set": update_data},
                upsert=True,
            )

            if result.upserted_id:
                print(f"New user {member} added to the database.")
            else:
                print(f"User {member}'s presence updated in the database.")

        except Exception as e:
            print(f"Error updating presence for user {member}: {str(e)}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            "RickBot_Watcher is ready. Processing all users and their presence data..."
        )
        for guild in self.bot.guilds:
            for member in guild.members:
                await self.process_user_if_opted_in(member)
        print("Finished processing all users and their presence data.")

    @commands.Cog.listener()
    async def on_user_update(self, _, user: discord.User):
        await self.process_user_if_opted_in(user)

    @commands.Cog.listener()
    async def on_presence_update(self, _, member: discord.Member):
        await self.process_user_if_opted_in(member)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.process_user_if_opted_in(member)


async def setup(
    bot: commands.Bot,
) -> NoReturn:
    await bot.add_cog(RickBot_Watcher(bot))
