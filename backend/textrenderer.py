import asyncio
import re
from backend.config import Config
from backend.keymanagement import get_info
import datetime
from hashlib import sha256
import random


# generate probabilitiscly unique id for each userline
def nextn():
    return sha256((str(datetime.datetime.now()) + str(random.randint(0, 256))).encode()).hexdigest()

# get user line
def get_user_line(prog, userkey):
    name, colour = get_info(userkey)
    index = nextn()
    try:
        prog.cache["colorindex"][index] = colour
    except Exception as e:
        try:
            prog.cache["colorindex"] = dict()
        except Exception as f:
            print(type(e), e, type(f), f)
            
        # prog.cache["colorindex"][index] = colour
    return "\n[color={}]{}[anchor={}][/color]    [size={}]{}[/size]\n".format(
        colour,
        name,
        index,
        Config.DATE_FONT_SIZE, datetime.datetime.now().strftime("%a %d %b %y  %I:%M %p"))

# replace charecter
def replace_charecters(text):
    text = text.replace("&bl;", "[").replace("&br;", "]").replace("&amp;", "&")
    return text

# find all jid addreesses in a string
def find_jids(text):
    jids = []
    for match in re.finditer(r'[\w\.-]+@[\w\.-]+', text):
        jids.append(match.group(0))
    return jids

# replace all jid addresses with a link
def replace_jids(text):
    for jid in set(find_jids(text)):
        text = text.replace(jid, "[ref={}]{}[/ref]".format(jid, heighlight(jid)))
    return text


# find all links in text
def find_links(text):
    links = []
    for match in re.finditer(r'(https?://[^\s]+)', text):
        links.append(match.group(0))
    return links

#replace all links with a link
def replace_links(text):
    for link in set(find_links(text)):
        text = text.replace(link, "[ref={}]{}[/ref]".format(link, heighlight(link)))
    return text

# render links and references to a pre render format
async def render_text(text):
    text = replace_charecters(text)
    text = replace_links(text)
    text = replace_jids(text)
    return text

def heighlight(raw):
    return " [color={}]{}[/color] ".format(Config.HEIGHLIGHT_COLOUR, raw)


# testing function
async def main():
    print(await render_text("user1@localhost is retarted motherfucker user1@localhost"))
    print("    ")
    print(await render_text("some text http://url.idk somemore text mabaybe http://another maybe more idk and replaces"))
    print(await render_text("some text https://url.idk somemore text mabaybe https://another maybe more idk and replaces"))
    print(await render_text("some text encrypted-msger://user_wquf8uewgf more message"))
    print(await render_text("some text encrypted-msger://msg_helo9825972398    more medssage"))
    print(await render_text("some text bob://msg_helo9825972398 more medssage"))
    print("    ")
    print(await render_text("some texthttp://url.idk somemore text mabaybe http://another maybe more idk and replaces"))
    print(await render_text("some texthttps://url.idk somemore text mabaybe https://another maybe more idk and replaces"))
    print(await render_text("some textencrypted-msger://user_wquf8uewgf more message"))
    print(await render_text("some textencrypted-msger://msg_helo9825972398    more medssage"))
    print(await render_text("some textbob://msg_helo9825972398 more medssage"))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())