import discord
import os
import sys
import subprocess

import bot
import logger

class Control(bot.Extension):
    @bot.dev()
    @bot.command()
    async def stop(ctx, message):
        """Shutdown the Bot"""
        await message.add_reaction("✅")
        logger.info(f"Shutdown by {message.author.display_name} ({message.author.id})")
        await ctx.bot.logout()

    @bot.command()
    async def restart(ctx, message):
        """Update the bot from Git and restart"""
        subprocess.getoutput("git pull")
        mid = await message.channel.send(embed=discord.Embed(
            title="Restarting",
            color=discord.Color.from_rgb(r=255, g=255, b=0)
        ))
        with open("/tmp/restart-bot", 'w') as f:
            f.write(str(message.channel.id)+"|"+str(mid.id))
        os.execl(sys.executable, sys.executable, *sys.argv)
        await ctx.bot.logout()

    @bot.event("on_ready")
    async def ready(ctx, _):
        if os.path.isfile("/tmp/restart-bot"):
            with open("/tmp/restart-bot") as f:
                data = f.read().split("|")
            channel = ctx.bot.get_channel(int(data[0]))
            message = await channel.get_message(int(data[1]))
            await message.edit(embed=discord.Embed(
                title="Restarted!",
                color=discord.Color.from_rgb(r=0, g=255, b=0)
            ))
            os.remove("/tmp/restart-bot")
