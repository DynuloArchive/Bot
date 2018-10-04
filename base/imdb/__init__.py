"""IMDb for Disco"""
import bot
import discord
from imdb import IMDb

ia = IMDb()

class IMDB(bot.Extension):
    """IMDb database"""

    @bot.argument("movie+")
    @bot.command()
    async def imdb(ctx, message):
        """Search for movies on IMDb"""
        async with message.channel.typing():
            movie = ia.search_movie(ctx.args.movie)[0]
            ia.update(movie)
            embed = discord.Embed(
                title=movie.get("title")+" ("+str(movie.get("year"))+")",
                url="https://imdb.com/title/tt"+str(movie.movieID),
                description=movie.get("plot")[0].rsplit("::", 1)[0].strip()
            )
            if "cover url" in movie:
                embed.set_thumbnail(url=movie.get("cover url"))
            if "directors" in movie:
                directors = []
                for director in movie.get("directors"):
                    directors.append(director['name'])
                embed.add_field(name="Director(s)", value=", ".join(directors))
        await message.channel.send(embed=embed)
