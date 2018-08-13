import sys
import os
import importlib
import inspect
import subprocess

import logger
import bot

class Extension:
    pass

class Extensions:
    @classmethod
    def get(cls, dir):
        extlist = []
        if sys.platform == "linux" or sys.platform == "linux2":
            extensions = [x[0].split('/')[1] for x in os.walk(dir) if x[0].count('/') == 1 and "__pycache__" not in x[0] and ".git" not in x[0]]
        else:
            extensions = [x[0].split('\\')[-1] for x in os.walk('./{}'.format(dir)) if x[0].count('/') == 1 and "__pycache__" not in x[0] and ".git" not in x[0]][1:]

        if not extensions:
            logger.warning("No extensions in {} directory".format(dir))

        for ext in extensions:
            extname = "{}.{}".format(dir, ext)
            if os.path.exists(os.path.join(dir, ext, "deps.txt")):
                install = False
                if not os.path.exists(".data/"):
                    os.mkdir(".data/")
                if not os.path.exists(os.path.join(".data/", dir)):
                    os.mkdir(os.path.join(".data/", dir))
                if not os.path.exists(os.path.join(".data/", dir, ext)):
                    os.mkdir(os.path.join(".data/", dir, ext))
                if os.path.exists(os.path.join(".data/", dir, ext, "deps.md5")):
                    with open(os.path.join(".data/", dir, ext, "deps.md5")) as dephash:
                        import hashlib
                        logger.debug("Comparing dependency hashes for {}".format(extname))
                        if hashlib.md5(open(os.path.join(dir, ext, "deps.txt"), 'rb').read()).hexdigest() != dephash.read().strip():
                            logger.info("Updating Dependencies for {}".format(extname))
                            install = True
                else:
                    install = True

                if install:
                    deps = ""
                    with open(os.path.join(dir, ext, "deps.txt")) as deptxt:
                        deps = deptxt.read().split("\n")
                    for dep in deps:
                        if dep.strip() != "":
                            logger.info("Installing {} for {}".format(dep, extname))
                            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep, '--upgrade', '--user'], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
                    import hashlib
                    with open(os.path.join(".data/", dir, ext, "deps.md5"), "w") as dephash:
                        dephash.write(hashlib.md5(open(os.path.join(dir, ext, "deps.txt"), 'rb').read()).hexdigest())

            try:
                ext = importlib.import_module(extname)
                logger.debug("  {}".format(extname))
            except Exception as e:
                logger.error("Load Failed: {}".format(extname))
                logger.error(str(e))
                continue
            clsmembers = inspect.getmembers(sys.modules[extname], inspect.isclass)
            for c in clsmembers:
                if issubclass(c[1], bot.Extension):
                    logger.debug("    {0[0]}".format(c))
                    c[1].commands = []
                    c[1].handlers = []
                    c[1].tasks    = []
                    c[1].fullname = str(c[1]).split("'",2)[1]
                    for method in inspect.getmembers(c[1]):
                        if isinstance(method[1], bot.Command):
                            c[1].commands.append(method[1])
                        elif isinstance(method[1], bot.EventHandler):
                            c[1].handlers.append(method[1])
                        elif isinstance(method[1], bot.Task):
                            c[1].tasks.append(method[1])
                    extlist.append(c[1])
        return extlist
