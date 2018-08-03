import bot
import discord
import logger

from contextlib import redirect_stdout
import io
import re
import sys
import traceback

class Client(discord.Client):
    async def on_connect(self):
        logger.debug("Connected to Discord")

    async def on_ready(self):
        logger.info("Connected as {0.name} ({0.id})".format(self.user), "green")
        self.extensions = []
        logger.info("Loading Base Extensions")
        self.base_extensions = bot.Extensions.get('base')
        logger.info("Loading {} Extensions from {}".format(self.profile.extensions, self.profile.hash))
        self.extensions = bot.Extensions.get("ext-{}".format(self.profile.hash)) + self.base_extensions
        logger.info("Ready", "green")

        #Start tasks
        for ext in self.extensions:
            for task in ext.tasks:
                await task.start(self, ext)

    async def execute(self, message, profile=False):
        if message.author.id == self.user.id:
            return
        if message.content.startswith(self.profile.prefix):
            raw = message.content[len(self.profile.prefix):].split()
        else:
            raw = message.content.split(" ", 2)[1:]
        cmd = raw[0].lower()
        args = " ".join(raw[1:])
        args = re.compile(r'''((?:[^\s"']|"[^"]*"|'[^']*')+)''').split(args)[1::2]
        new = []
        for arg in args:
            new.append(arg.strip("\""))
        args = new
        for ext in self.extensions:
            for c in ext.commands:
                if c.name == cmd:
                    if bot.in_role_list(message.author, c.roles):
                        if profile:
                            import pprofile
                            profiler = pprofile.Profile()
                            with profiler():
                                await self.command(c, bot.Context(self, ext, message), args)
                            out = io.StringIO()
                            with redirect_stdout(out):
                                profiler.print_stats()
                            resp = out.getvalue().split("\n")
                            await bot.send_stats(c, self.profile.prefix, resp, raw, message.channel)
                        else:
                            await self.command(c, bot.Context(self, ext, message), args)
                    else:
                        await message.channel.send("You are not allowed to run that command.")

    async def command(self, c, ctx, args):
        try:
            logger.debug("Attempting to run {}".format(c.name))
            await c.run(ctx, args)
        except Exception:
            #exc_type, exc_obj, exc_tb = sys.exc_info()
            tb = traceback.format_exc()
            if self.profile.mode == "live":
                await ctx.message.channel.send("Oh no! :cry: An error occurred. It has been reported to the Code Contributers.")
                channel = discord.utils.find(lambda c: c.name == "errors", ctx.message.guild.channels)
            else:
                channel = ctx.message.channel
            await channel.send(
                "An error occured during the execution of `{}` by {} in {}\n\n```py\n{}\n```"
                .format(ctx.message.content, ctx.message.author.display_name, ctx.message.channel.mention, tb)
            )
            logger.error("An error occured: "+str(tb))

    async def on_message(self, message):
        await self.wait_until_ready()
        if message.author.id == self.user.id:
            return
        if (message.content.startswith(self.profile.prefix) and message.content.replace(self.profile.prefix, "").strip() != "") or (message.content.startswith(self.user.mention)):
            await self.execute(message)
        elif message.content.startswith("profile{}".format(self.profile.prefix)):
            message.content = message.content[7:]
            await self.execute(message, profile = True)
        else:
            await self.fire_event(message, "on_message")

    async def on_message_delete(self, message):
        await self.fire_event(message, "on_message_delete")

    async def on_message_edit(self, before, after):
        await self.fire_event([before, after], "on_message_edit")

    async def on_reaction_add(self, reaction, user):
        await self.fire_event([reaction, user], "on_reaction_add")

    async def on_reaction_remove(self, reaction, user):
        await self.fire_event([reaction, user], "on_reaction_remove")

    async def on_reaction_clear(self, message, reactions):
        await self.fire_event([message, reactions], "on_reaction_clear")

    async def on_member_join(self, member):
        await self.fire_event(member, "on_member_join")

    async def on_member_remove(self, member):
        await self.fire_event(member, "on_member_remove")

    async def on_member_update(self, before, after):
        await self.fire_event([before, after], "on_member_update")

    async def fire_event(self, args, event):
        await self.wait_until_ready()
        for ext in self.extensions:
            for h in ext.handlers:
                if h.event == event:
                    try:
                        if h.dev and self.profile.mode == "test":
                            await h.run(bot.Context(self, ext, args))
                        else:
                            if h.live:
                                if self.profile.mode == "live":
                                    await h.run(bot.Context(self, ext, args))
                            else:
                                await h.run(bot.Context(self, ext, args))
                    except Exception:
                        tb = traceback.format_exc()
                        channel = None
                        if channel:
                            await channel.send(
                                "An error occured during the execution of `{}` by {} in {}\n\n```py\n{}\n```"
                                .format(ctx.message.content, ctx.message.author.display_name, ctx.message.channel.mention, tb)
                            )
                        logger.error("An error occured: "+str(tb))
