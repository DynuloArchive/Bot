"""Search Engines for Disco"""
import discord
from google import google
import bot

class Searches(bot.Extension):
    """Search Engines"""

    @bot.argument("query+")
    @bot.command()
    async def google(ctx, message):
        """Search for stuff on Google"""
        async with message.channel.typing():
            results = google.search(ctx.args.query)
            embed = discord.Embed(
                title="Google Search Results",
                description=f"Search results for `{ctx.args.query}`"
            )
            for result in results[0:3]:
                embed.add_field(name=result.name, value=f"[{result.description}]({result.link})")
        await message.channel.send(embed=embed)
