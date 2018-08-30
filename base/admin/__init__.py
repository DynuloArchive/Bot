"""Commands for admins"""
import discord
import bot

class Admin(bot.Extension):
    """Provides information about the Bot and loaded extensions"""

    @bot.argument("[channel]", discord.TextChannel, "here")
    @bot.argument("text+", str)
    @bot.command()
    async def speak(ctx, message):
        """Says something in the specified channel"""
        await ctx.args.channel.send(ctx.args.text)
        await message.add_reaction("✅")

    @bot.role("moderator")
    @bot.argument("channel*", discord.TextChannel, "here")
    @bot.command()
    async def lock(ctx, message):
        """Locks the specified or current channel"""
        everyone = discord.utils.find(lambda m: m.name.lower() == "@everyone", message.channel.guild.roles)
        perms = ctx.args.channel.overwrites_for(everyone)
        perms.send_messages = False
        await ctx.args.channel.set_permissions(everyone, overwrite=perms)
        await message.add_reaction("🔒")

    @bot.role("moderator")
    @bot.argument("channel*", discord.TextChannel, "here")
    @bot.command()
    async def unlock(ctx, message):
        """Unlocks the specified or current channel"""
        everyone = discord.utils.find(lambda m: m.name.lower() == "@everyone", message.channel.guild.roles)
        perms = ctx.args.channel.overwrites_for(everyone)
        perms.send_messages = None
        await ctx.args.channel.set_permissions(everyone, overwrite=perms)
        await message.add_reaction("🔓")
