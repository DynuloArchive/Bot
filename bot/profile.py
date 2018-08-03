import sys
import os
import discord

import logger

class Profile:
    """The profile for the current bot"""
    def __init__(self, data):
        for req in ["name", "mode", "prefix", "tokens", "extensions", "color"]:
            if req not in data:
                logger.error("Invalid Profile: Missing '{}'".format(req))
                sys.exit(2)

        if data["mode"] not in ["dev", "live"]:
            logger.error("Invalid Profile Mode: {}".format(data["mode"]))
            sys.exit(3)

        data["source"], data["extensions"] = data["extensions"].split(":", 1)

        if data["source"] not in ["github", "local"]:
            logger.error("Invalid Extension Source: {}".format(data["source"]))
            sys.exit(4)

        self.name = data["name"]
        self.mode = data["mode"]
        self.prefix = data["prefix"]
        self.tokens = data["tokens"]
        self.extensions = os.path.expanduser(data["extensions"])
        self.source = data["source"]
        self.color = discord.Colour.from_rgb(
            r=data["color"][0],
            g=data["color"][1],
            b=data["color"][2]
        )
        import hashlib
        self.hash = hashlib.md5(self.extensions.encode("UTF-8")).hexdigest()

    def fetch(self):
        """If the extensions are from a remote source, fetch them"""
        if self.source == "github":
            logger.debug("Updating {} from Git".format(self.extensions))
            path = "ext-{}".format(self.hash)
            if not os.path.exists(path):
                logger.info("Cloning {}".format(self.extensions))
                os.system("git clone https://github.com/{} {} > /dev/null".format(self.extensions, path))
                if not os.path.exists("{}/__init__.py".format(path)):
                    open("{}/__init__.py".format(path), 'a').close()
            else:
                os.chdir(path)
                os.system("git pull > /dev/null")
                os.chdir("../")

        elif self.source == "local":
            if os.path.exists("ext-{}".format(self.hash)):
                os.remove("ext-{}".format(self.hash))
            logger.debug("Preparing Local Folder")
            os.symlink(self.extensions, "ext-{}".format(self.hash))
