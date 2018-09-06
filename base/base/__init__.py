import bot
import discord
import math
import os
import logger

class Info(bot.Extension):
    """Provides information about the Bot and loaded extensions"""

    @bot.command()
    async def info(ctx, message):
        """Displays info about the bot or a command"""
        embed = discord.Embed()
        embed.add_field(name="Profile", value=ctx.profile.name)
        embed.add_field(name="Mode", value=ctx.profile.mode)
        embed.set_author(name=ctx.user.name, icon_url=ctx.user.avatar_url)
        await message.channel.send(embed=embed)

class Help(bot.Extension):
    """Helps people use the bot"""

    @bot.argument("command*", bot.Command)
    @bot.command()
    async def help(ctx, message):
        """Displays help information"""
        if ctx.args.command == None:
            m = "```makefile\n"
            commands = []
            for ext in ctx.bot.extensions:
                commands += ext.commands
            commands.sort()
            for i in range(0, 6):
                try:
                    m += commands[i].name + ":\n    " + commands[i].help + "\n"
                except TypeError:
                    m += commands[i].name + "\n\n"
            embed = discord.Embed(
                title="Help",
                description=m+"```",
                color=ctx.profile.color
            )
            embed.set_footer(text="Help Page: 1")
            mid = await message.channel.send(embed=embed)
            await mid.add_reaction("\u2B05")
            await mid.add_reaction("\u27A1")
            await mid.add_reaction("❌")
        else:
            embed = discord.Embed(
                title="{0.profile.prefix}{0.args.command.name} {0.args.command.usage}".format(ctx),
                description=ctx.args.command.help,
                url="https://github.com/Synixe/Bot/blame/master/{0}#L{1.start}L{1.end}".format(ctx.args.command.file.replace(os.getcwd(), ""), ctx.args.command)
            )
            embed.set_footer(text=ctx.args.command.extension.fullname + "." + ctx.args.command.name)
            await message.channel.send(embed=embed)

    @bot.event("on_reaction_add")
    async def change_page(ctx, args):
        reaction, member = args
        if member.id == ctx.bot.user.id:
            return

        if len(reaction.message.embeds) == 1:
            try:
                if reaction.message.embeds[0].footer.text.startswith("Help Page: "):
                    commands = []
                    for ext in ctx.bot.extensions:
                        commands += ext.commands
                    commands.sort()
                    if reaction.emoji == "❌":
                        await reaction.message.edit(content="Help Closed", embed=None)
                        await reaction.message.clear_reactions()
                        return
                    page = int(reaction.message.embeds[0].footer.text.split(": ")[-1])
                    if reaction.emoji == "⬅":
                        page -= 1
                    elif reaction.emoji == "➡":
                        page += 1
                    if page == 0:
                        page = math.ceil(len(commands) / 6)
                    if page > math.ceil(len(commands) / 6):
                        page = 1
                    m = "```makefile\n"
                    for i in range(0 + (6 * (page - 1)),6 * (page)):
                        try:
                            m += commands[i].name + ":\n    " + commands[i].help + "\n"
                        except:
                            pass
                    embed = discord.Embed(
                        title="Command Browser",
                        description=m+"```",
                        color=discord.Colour.from_rgb(r=255, g=192, b=60)
                    )
                    embed.set_footer(text="Help Page: "+str(page))
                    await reaction.message.clear_reactions()
                    await reaction.message.edit(embed=embed)
                    await reaction.message.add_reaction("\u2B05")
                    await reaction.message.add_reaction("\u27A1")
                    await reaction.message.add_reaction("❌")
                else:
                    return
            except AttributeError:
                return
