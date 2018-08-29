"""Parses arguments using argparse and then converts them into various formats"""

import argparse
import datetime
import io
from contextlib import redirect_stderr
import discord

import bot
import logger

class ArgumentException(Exception):
    """Base class for ArgumentsExceptions"""
    def __init__(self, text, data):
        super().__init__(text)
        self.data = data

class Arguments:
    """A list of Arguments for a Command"""
    def __init__(self, ctx, raw, args):
        self._ctx = ctx
        self._raw = raw
        self._args = args

        self._parser = argparse.ArgumentParser(description="Placeholder Text")

        for arg in self._args:
            nargs = ""
            argname = arg[0]
            if "+" in argname and "[" in argname:
                raise Exception("Argument can't have both + and [], use * instead")
            #MUTLIWORD FLAG
            for flag in ["+","*"]:
                if flag in argname:
                    nargs = flag
                    argname = argname.replace(flag, "")
            default = arg[2]
            #FLAG
            if argname.startswith("(") and arg[0].endswith(")"):
                if arg[1] != None:
                    logger.error(f"Flag {argname} can not have type {arg[1]}, must be None")
                logger.debug(f"Adding FLAG argument {argname[1:-1]}")
                self._parser.add_argument(f"--{argname[1:-1]}", action='store_true', default=default)
            #OPTIONAL
            elif argname.startswith("[") and argname.endswith("]"):
                nargs = "?"
                logger.debug(f"Adding optional argument {argname} with nargs=\"{nargs}\"")
                self._parser.add_argument(f"--{argname[1:-1]}", type=str, nargs=nargs, default=default)
            #REQUIRED
            else:
                if nargs != "":
                    logger.debug(f"Adding argument {argname} with nargs=\"{nargs}\"")
                    self._parser.add_argument(argname, type=str, nargs=nargs, default=default)
                else:
                    logger.debug(f"Adding argument {argname}")
                    self._parser.add_argument(argname, type=str, default=default)

        err = io.StringIO()
        with redirect_stderr(err):
            try:
                for arg, value in self._parser.parse_args(raw).__dict__.items():
                    for base in self._args:
                        if base[0] == arg or base[0][1:-1] == arg or base[0] == arg+"+" or base[0] == arg+"*":
                            if type(value) == list:
                                if len(value) == 1:
                                    value = value[0]
                                elif not value:
                                    value = None
                            value = self._parse(base, value)
                            break
                    setattr(self, arg, value)
            except SystemExit as e:
                logger.error(f"Exit code {str(e)} from parse_args")
                if str(e) == "2":
                    missing = err.getvalue().split("\n")[1].split(":",2)[-1].strip()
                    logger.error(f"Missing: {missing}")
                    raise ArgumentException("Not Enough Args", [self, argname])

    def usage(self):
        """Return the usage string"""
        usage = io.StringIO()
        self._parser.print_help(usage)
        return usage.getvalue().split("\n")[5].strip()

    def _parse(self, arg, value):
        argtype = arg[1]
        arg = arg[0]
        if argtype == bot.Command:
            if value == None:
                return None
            for ext in self._ctx.bot.extensions:
                for command in ext.commands:
                    if command.name == value:
                        command.extension = ext
                        return command
            raise ArgumentException("Invalid Command", [self, arg, value])
        elif argtype == discord.Member:
            if value == "author":
                return self._ctx.message.author
            if value.startswith("<@"):
                value = value[2:-1]
                if value.startswith("!"):
                    value = value[1:]
            try:
                value = int(value)
                member = self._ctx.message.channel.guild.get_member(value)
            except ValueError:
                value = value.lower()
                member = discord.utils.find(lambda m: m.name.lower() == value or m.display_name.lower() == value, self._ctx.message.channel.guild.members)
            if member is None:
                raise ArgumentException("Member Not Found", [self, arg, value])
            return member
        elif argtype == discord.TextChannel:
            if value == "here":
                return self._ctx.message.channel
            if value.startswith("<#"):
                value = value[2:-1]
            try:
                value = int(value)
                channel = discord.utils.find(lambda c: c.id == value, self._ctx.message.channel.guild.channels)
            except ValueError:
                value = value.lower()
                channel = discord.utils.find(lambda c: c.name.lower() == value, self._ctx.message.channel.guild.channels)
            if channel is None:
                raise ArgumentException("Channel Not Found", [self, arg, value])
            return channel
        elif argtype == discord.Role:
            role = discord.utils.find(lambda m: m.name.lower() == value.lower() or str(m.id) == value, self._ctx.message.channel.guild.roles)
            if role is None:
                raise ArgumentException("Role Not Found", [self, arg, value])
            return role
        elif argtype == datetime.tzinfo:
            import pytz
            if value is None:
                return None
            if value in pytz.all_timezones:
                return pytz.timezone(value)
            else:
                for tz in pytz.all_timezones:
                    if value.replace(" ", "_").lower() in tz.lower():
                        return pytz.timezone(tz)
            raise ArgumentException("Timezone Not Found", [self, arg, value])
        elif argtype == int:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = self._txt2int(value)
                except:
                    raise ArgumentException("TypeError", [self, arg, value, "number"])
            except TypeError:
                try:
                    if type(value) == list and len(value) == 1:
                        value = int(value[0])
                    else:
                        raise Exception()
                except Exception:
                    try:
                        value = self._txt2int(" ".join(value))
                    except Exception:
                        raise ArgumentException("TypeError", [self, arg, value, "number"])
        elif argtype == str:
            if type(value) == list:
                return " ".join(value)
        return value

    def _txt2int(self, textnum):
        """Converts text into an int: "ten" -> 10"""
        numwords = {}
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        scales = ["hundred", "thousand", "million", "billion", "trillion"]
        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)
        current = result = 0
        for word in textnum.split():
            if word not in numwords:
                raise Exception("Illegal word: " + word)
            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
        return result + current
