"""Logs to a file and outputs to the console with colors"""
import datetime
import time
import sys
import os
import emoji

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf8', buffering=1)

DEBUG = False

def clear():
    """Empty the log file"""
    if not os.path.exists("logs/"):
        os.mkdir("logs/")
    with open("logs/bot.log", 'w') as botlog:
        botlog.write("")
    with open("logs/botdebug.log", 'w') as debuglog:
        debuglog.write("")

def dwrite(tag, text):
    text = "["+tag+"]["+datetime.datetime.fromtimestamp(time.time()).strftime('%d %H:%M:%S')+"] " + str(text)
    with open("logs/botdebug.log", 'a', encoding="utf-8") as debuglog:
        debuglog.write(text+"\n")

def info(text, c="grey"):
    """Info, Always Displayed"""
    color(c)
    write("INFO", text)
    color("reset")

def warning(text, c="yellow"):
    """Info, Always Displayed"""
    color(c)
    write("WARN", text)
    color("reset")

def error(text, c="red"):
    """Error, Always Displayed"""
    color(c)
    write("ERRO", text)
    color("reset")

def debug(text, c="blue"):
    """Debug Information"""
    if DEBUG:
        color(c)
        write("DBUG", text)
        color("reset")
    else:
        dwrite("DBUG", text)

def set_debug(debug):
    """Set the debug setting"""
    global DEBUG
    DEBUG = debug

def color(col):
    """Set the text color"""
    if col == "red":
        sys.stdout.write('\033[91m')
    elif col == "green":
        sys.stdout.write('\033[92m')
    elif col == "yellow":
        sys.stdout.write('\033[93m')
    elif col == "blue":
        sys.stdout.write('\033[94m')
    elif col == "reset":
        sys.stdout.write('\033[0m')

def write(tag, text):
    """Write to the log file"""
    otext = text
    text = "["+tag+"]["+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')+"] " + str(text)
    sys.stdout.write(emoji.emojize(text, use_aliases=True)+"\n")
    sys.stdout.flush()
    with open("logs/bot.log", 'a', encoding="utf-8") as botlog:
        botlog.write(text+"\n")
    dwrite(tag, otext)

def loading(text):
    sys.stdout.write(emoji.emojize(text, use_aliases=True))
