import bot
import discord
import math
import os
import logger

class Admin(bot.Extension):
    """Provides information about the Bot and loaded extensions"""

    @bot.argument("[channel]", discord.TextChannel, "here")
    @bot.argument("text+", str)
    @bot.command()
    async def speak(ctx, message):
        """Says something in the specified channel"""
        await ctx.args.channel.send(ctx.args.text)
        await message.add_reaction("✅")
