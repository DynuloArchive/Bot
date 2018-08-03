import bot
import logger

import asyncio
import inspect

class Task:
    """A task that is run continuously"""
    def __init__(self, name, callback, **kwargs):
        self.func = callback
        self.name = name

        self.time = kwargs.get("time")

        self.live = False
        self.dev = False

        self.file = kwargs.get("file")
        self.lineno = kwargs.get("lineno")
        self.help = kwargs.get("help")

    async def start(self, client, ext):
        """Attempts to start the task if applicable"""
        if self.dev and client.profile.mode == "test":
            await self.run(client, ext)
        elif self.live:
            if client.profile.mode == "live":
                await self.run(client, ext)
        else:
            await self.run(client, ext)

    async def run(self, client, ext):
        """Runs the task"""
        logger.debug("Starting {}".format(self.name))
        while not client.is_closed():
            client.loop.create_task(self.func(bot.Context(client, ext, None)))
            await asyncio.sleep(self.time)

def task(time, **attrs):
    """Decorator for creating a Task"""
    def decorator(func):
        frame = inspect.stack()[1]
        attrs["file"] = frame[1]
        attrs["lineno"] = frame[2]
        attrs["time"] = time
        if isinstance(func, Task):
            raise TypeError("Callback is already a task.")
        import asyncio
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")
        help_doc = attrs.get('help')
        if help_doc is not None:
            help_doc = inspect.cleandoc(help_doc)
        else:
            help_doc = inspect.getdoc(func)
            if isinstance(help_doc, bytes):
                help_doc = help_doc.decode('utf-8')
        attrs['help'] = help_doc
        return Task(name=func.__name__, callback=func, **attrs)
    return decorator
