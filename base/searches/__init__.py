"""Search Engines for Disco"""
import discord
from google import google
import bot
import urbandictionary as ud
from PyDictionary import PyDictionary

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

    @bot.argument("query+")
    @bot.command()
    async def urban(ctx, message):
        """Search for stuff on Urban Dictionary"""
        try:
            async with message.channel.typing():
                defs = ud.define(ctx.args.query)[0]
            await message.channel.send(defs.definition)
        except IndexError:
            await message.channel.send("No definiton was found 😢")

    @bot.argument("query+")
    @bot.command()
    async def define(ctx, message):
        """Get the definition of a word"""
        dictionary = PyDictionary()
        embeds = []
        try:
            async with message.channel.typing():
                definition = dictionary.meaning(ctx.args.query)
                for usage, defs in definition.items():
                    query = ctx.args.query.title()
                    usage = usage.lower()
                    embed = discord.Embed(
                        title=f"{query}: {usage}",
                        description=" -  " + ("\n -  ".join(defs[0:min(3,len(defs))]))
                    )
                    embeds.append(embed)
            for e in embeds:
                await message.channel.send(embed=e)
        except AttributeError:
            await message.channel.send("No definition was found 😢")
