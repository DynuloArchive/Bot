"""Games for Disco"""
import random
import asyncio
import requests
import discord
import bot

class SimpleGames(bot.Extension):
    """Games for Disco"""

    @bot.command()
    async def flip(ctx, message):
        """Flip a coin"""
        side = random.randint(0, 1)
        if side == 0:
            output = "It lands on heads"
        else:
            output = "It lands on tails"
        await message.channel.send(output)

    @bot.argument("sides*", int, default=6)
    @bot.command()
    async def dice(ctx, message):
        """Roll a dice"""
        await message.channel.send(random.choice(
            ["The value is {0}", "You rolled a {0}", "It lands on {0}"]
        ).format(random.randint(1, ctx.args.sides)))

    @bot.argument("choice")
    @bot.command()
    async def rps(ctx, message):
        """Rock, Paper, Scissors Game"""
        valid = ["Rock", "Paper", "Scissors"]
        if not ctx.args.choice.title() in valid:
            await message.channel.send("That is not a valid choice")
            return
        botchoice = random.randint(0, 2)
        output = valid[botchoice]
        player = valid.index(ctx.args.choice.lower())
        if player == botchoice:
            output += ", it's a tie."
        elif player == botchoice - 1 or player == botchoice + 2:
            output += ", you lose."
        elif player == botchoice + 1 or player == botchoice - 2:
            output += ", you win."
        await message.channel.send(output)

    @bot.command()
    async def joke(ctx, message):
        """Prints a joke"""
        joke = requests.get("https://08ad1pao69.execute-api.us-east-1.amazonaws.com/dev/random_joke").json()
        await message.channel.send(joke["setup"])
        await asyncio.sleep(4)
        await message.channel.send(joke["punchline"])

    @bot.argument("meme")
    @bot.argument("top")
    @bot.argument("bottom")
    @bot.command()
    async def meme(ctx, message):
        """Prints a formattable meme"""
        escapes = {
            "-": "--",
            "_": "__",
            " ": "_",
            "?": "~q",
            "%": "~p",
            "#": "~h",
            "/": "~s",
            "\"": "''"
        }
        meme = ctx.args.meme
        toptext = ctx.args.top
        bottomtext = ctx.args.bottom
        for a, b in escapes.items():
            meme = meme.replace(a,b)
            toptext = toptext.replace(a,b)
            bottomtext = bottomtext.replace(a,b)
        embed = discord.Embed(
            color=discord.Color.from_rgb(r=255, g=255, b=0)
        )
        embed.set_image(url=f"https://memegen.link/{meme}/{toptext}/{bottomtext}.jpg")
        embed.set_footer(text=f"Created by: {message.author.display_name}")
        await message.delete()
        await message.channel.send(embed=embed)
