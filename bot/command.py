import discord
import inspect

import logger

from bot.arguments import Arguments, ArgumentException

class Command:
    """A Discord command for the Bot"""

    def __lt__(self, other):
        return self.name < other.name

    def __init__(self, name, callback, **kwargs):
        self.func = callback
        self.name = name

        self.dev = False
        self.live = False

        self.roles = ["@everyone"]
        self.args = []
        self.usage = " ".join([x[0] for x in self.args])

        self.file = kwargs.get("file")
        self.help = kwargs.get("help")

        with open(self.file, encoding="utf-8") as source:
            lines = source.read().split("\n")
            for lno, line in enumerate(lines):
                if line.strip().startswith("async def {}(".format(self.func.__name__)):
                    for i in range(lno - 1, 0, -1):
                        if lines[i].strip().startswith("@"):
                            self.start = i + 1
                        else:
                            break
                    self.end = len(lines) - 1
                    for i in range(lno, len(lines)):
                        if lines[i].strip().startswith("@") or lines[i].strip().startswith("class "):
                            self.end = i - 1
                            break

    async def run(self, ctx, args):
        """Executes the command"""
        if self.args == []:
            ctx.args = None
            await self.func(ctx, ctx.message)
            return
        try:
            ctx.args = Arguments(ctx, args, self.args)
            if self.dev:
                if ctx.profile.mode == "dev":
                    logger.debug(f"Running {self.name}")
                    await self.func(ctx.safe(), ctx.message)
                await ctx.message.channel.send("That command is only available in dev mode.")
            elif self.live:
                if ctx.profile.mode == "live":
                    logger.debug(f"Running {self.name}")
                    await self.func(ctx.safe(), ctx.message)
                await ctx.message.channel.send("That command is only available in live mode.")
            else:
                logger.debug(f"Running {self.name}")
                await self.func(ctx.safe(), ctx.message)
                logger.debug(f"Exited {self.name}")
        except ArgumentException as e:
            logger.error("Handling {}".format(str(e)))
            if str(e) == "Display Help":
                embed = discord.Embed(
                    title="{0._ctx.profile.prefix}{1} {2}".format(e.data[0], self.name, e.data[0].usage())
                )
                for arg in self.args:
                    if arg[2] is None:
                        embed.add_field(name=arg[0], value=str(arg[1]).split("'")[1])
                    else:
                        embed.add_field(name=arg[0], value="{} ({})".format(str(arg[1]).split("'")[1], arg[2]))
            elif str(e) == "Invalid Command":
                embed = discord.Embed(
                    title="Command Not Found",
                    description="The command `{}` provided for `{}` was not found".format(e.data[2], e.data[1])
                )
                embed.set_footer(text="Usage: {0._ctx.profile.prefix}{1} {2}".format(e.data[0], self.name, e.data[0].usage()))
            elif str(e) == "Not Enough Args":
                embed = discord.Embed(
                    title="Missing {}".format(e.data[1]),
                    description="`{}` is a required field".format(e.data[1])
                )
                embed.set_footer(text="Usage: {0._ctx.profile.prefix}{1} {2}".format(e.data[0], self.name, e.data[0].usage()))
            elif str(e) == "Member Not Found":
                embed = discord.Embed(
                    title="Member Not Found",
                    description="The user `{}` was not found.".format(e.data[2])
                )
            elif str(e) == "Channel Not Found":
                embed = discord.Embed(
                    title="Channel Not Found",
                    description="The channel `{}` was not found".format(e.data[2])
                )
            elif str(e) == "Role Not Found":
                embed = discord.Embed(
                    title="Role Not Found",
                    description="The role `{}` was not found.".format(e.data[2])
                )
            elif str(e) == "TypeError":
                embed = discord.Embed(
                    title="Invalid Type",
                    description="`{}` must be a {}".format(e.data[1], e.data[3])
                )
            elif str(e) == "Timezone Not Found":
                embed = discord.Embed(
                    title="Timezone Not Found",
                    description="`{}` is not a valid timezone. You can visit <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List> to see a list of valid timezones.".format(e.data[2])
                )
            await ctx.message.channel.send(embed=embed)

def command(name=None, **attrs):
    """Decorator to create a command from a function"""
    def decorator(func):
        frame = inspect.stack()[1]
        attrs["file"] = frame[1]
        attrs["lineno"] = frame[2]
        if isinstance(func, Command):
            raise TypeError('Callback is already a command.')
        import asyncio
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Callback must be a coroutine.')
        help_doc = attrs.get('help')
        if help_doc is not None:
            help_doc = inspect.cleandoc(help_doc)
        else:
            help_doc = inspect.getdoc(func)
            if isinstance(help_doc, bytes):
                help_doc = help_doc.decode('utf-8')
        attrs['help'] = help_doc
        fname = name or func.__name__
        return Command(name=fname, callback=func, **attrs)
    return decorator

def role(role):
    """Decorator to limit a command to specified roles"""
    def decorator(func):
        if len(func.roles) == 1 and func.roles[0] == "@everyone":
            func.roles = [role]
        else:
            func.roles.append(role)
        return func
    return decorator

def argument(name, argtype=str, default=None):
    """Decorator to define an argument for a command"""
    def decorator(func):
        if len(func.args) != 0 and ("+" in name or "*" in name):
            raise Exception("Unexpceted argument after multi-length argument")
        func.args.insert(0, [name, argtype, default])
        func.usage = " ".join([x[0] for x in func.args])
        return func
    return decorator

def dev():
    """Decorator to limit a command to dev mode only"""
    def decorator(func):
        if func.live:
            raise Exception("Function can't be both dev and live only")
        func.dev = True
        return func
    return decorator

def live():
    """Decorator to limit a command to live mode only"""
    def decorator(func):
        if func.dev:
            raise Exception("Function can't be both dev and live only")
        func.live = True
        return func
    return decorator
