"""Creating Polls for Disco"""
import discord
import bot
import logger

class Polls(bot.Extension):
    """Polls for Disco"""

    @bot.argument("[options]")
    @bot.argument("[type]", "str", "thumbs")
    @bot.argument("[title]")
    @bot.argument("text+")
    @bot.command()
    async def poll(ctx, message):
        """Create a simple Thumbsup or Thumbsdown poll"""
        embed = discord.Embed(
            title=ctx.args.title or "Poll",
            color=discord.Colour.from_rgb(r=255, g=192, b=60),
            description=ctx.args.text
        )
        embed.set_footer(text="Created by: {}".format(message.author.display_name))
        msg = await message.channel.send(embed=embed)
        if ctx.args.type == "thumbs":
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
        elif ctx.args.type == "runoff":
            EMOJI = ["1\u20e3","2\u20e3","3\u20e3","4\u20e3","5\u20e3"]
            if ctx.args.options == None:
                await message.channel.send("No options were provided.")
                await msg.delete()
                return
            else:
                options = ctx.args.options.split(",")
                if len(options) > 5:
                    await message.channel.send("Maximum 5 options")
                    await msg.delete()
                    return
                for option in options:
                    opt = await message.channel.send(option)
                    for i in range(len(options)):
                        await opt.add_reaction(EMOJI[i])

        await message.delete()

    @bot.argument("message")
    @bot.command()
    async def tally(ctx, message):
        ballots = {}
        spoiled = []
        alloptions = []
        msg = await message.channel.get_message(int(ctx.args.message))
        await message.add_reaction("✅")
        async for option in message.channel.history(after=msg, limit=5):
            def check(emoji,message):
                for r in message.reactions:
                    if r.emoji == emoji:
                        return True
                return False
            if check("1\u20e3",option):
                alloptions.append(option.id)
                logger.debug(f"Counting {option.content}")
                for reaction in option.reactions:
                    async for user in reaction.users():
                        if user.id == ctx.bot.user.id:
                            continue
                        if user in spoiled:
                            continue
                        if user in ballots:
                            if reaction.emoji in ballots[user]:
                                logger.error(f"Spoiled ballet from {user.display_name}")
                                spoiled.append(user)
                            else:
                                logger.debug(f"User {user.display_name} used vote {reaction.emoji}")
                                ballots[user][reaction.emoji] = option.id
                        else:
                            logger.debug(f"User {user.display_name} used vote {reaction.emoji}")
                            ballots[user] = {reaction.emoji: option.id}
        logger.debug(ballots)

        eliminated = []
        solved = False
        roundnum = -1
        while not solved:
            roundnum += 1
            round = {}
            total = 0
            logger.debug(f"Computing round {roundnum}")
            for user in ballots:
                if user in spoiled:
                    logger.debug(f"Ignore spolied ballot from {user.display_name}")
                    continue
                choices = ballots[user]
                counted = 0
                for index in ["1\u20e3","2\u20e3","3\u20e3","4\u20e3","5\u20e3"]:
                    if index not in ballots[user]:
                        logger.debug(f"Ballot from {user.display_name} does not contain index")
                        continue
                    if ballots[user][index] in eliminated:
                        logger.debug(f"Ballot from {user.display_name} is eliminated")
                        continue
                    logger.debug(f"Counting ballot from {user.display_name}")
                    total += 1
                    if ballots[user][index] in round:
                        round[ballots[user][index]] += 1
                    else:
                        round[ballots[user][index]] = 1
                    counted += 1
                    if counted == 2:
                        break
            for option in round:
                logger.debug(f"{option} had {round[option]} votes out of {(total + 1) / 2}")
                if round[option] > (total + 1) / 2:
                    solved = True
                    winner = await message.channel.get_message(option)
                    await message.channel.send(f"Winner is {winner.content}")
                    return
            lowest = total
            elim = None
            for option in alloptions:
                if option not in round and option not in eliminated:
                    elim = option
                    lowest = 0
                    break
                if option not in round:
                    continue
                if round[option] < lowest:
                    elim = option
                    lowest = round[option]
            if elim != None:
                removed = await message.channel.get_message(elim)
                logger.error(f"Eliminating {removed.content}")
                eliminated.append(elim)
            else:
                await message.channel.send("Inconclusive 🙅")
                solved = True
