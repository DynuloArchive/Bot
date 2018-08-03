import discord

from bot.arguments import Arguments, ArgumentException
from bot.command import Command, command, role, dev, live, argument
from bot.events import EventHandler, event
from bot.profile import Profile
from bot.context import Context
from bot.task import Task, task
from bot.extension import Extension, Extensions

def in_role_list(member, roles):
    """Check if a member is in a list of roles"""
    if "@everyone" in roles:
        return True
    if isinstance(member, discord.User):
        return False
    for r in member.roles:
        if r.name.lower() in roles:
            return True
    return False

async def send_stats(c, prefix, resp, raw, channel):
    """Sends performance statistics to Discord"""
    printing = False
    header = False
    inside = False
    text = ""
    info = ""
    for line in resp:
        if line.strip().startswith("File: {}".format(c.file)):
            printing = True
        elif line.strip().startswith("File:"):
            printing = False
        elif printing and line.startswith("----"):
            header = True
        if printing and not header:
            if not line.startswith("Line #"):
                info += line + "\n"
        elif printing and not inside:
            if line.split("|",1)[0].strip() == str(c.start - 1):
                inside = True
        elif printing and inside:
            if line.split("|",1)[0].strip() == str(c.end + 1):
                inside = False
            if inside:
                fields = line.split("|")
                data = [x.strip() for x in fields[:-1]]
                if len(data) == 0:
                    continue
                if data[0] != "(call)":
                    data.append(fields[-1][4:])
                else:
                    try:
                        data.append("#"+fields[-1].split("site-packages/")[1])
                    except IndexError:
                        data.append("#"+fields[-1])
                del fields
                dec =  "{}{}: {} ({}, {})".format(data[0], " " * (6 - len(data[0])), data[1], data[2], data[4])
                text += "{}{}| {}".format(dec, " " * (30 - len(dec)), data[-1]) + "\n"
    embed = discord.Embed(
        title="{}{} {}".format(prefix, c.name, " ".join(raw[1:])),
        description=info
    )
    await channel.send("```py\n"+text+"```", embed=embed)
