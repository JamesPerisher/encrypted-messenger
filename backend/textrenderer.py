import asyncio
import re
from backend.config import Config

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
    for jid in find_jids(text):
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
    for link in find_links(text):
        text = text.replace(link, "[ref={}]{}[/ref]".format(link, heighlight(link)))
    return text

# render links and references to a pre render format
async def render_text(text):
    text = replace_charecters(text)
    text = replace_jids(text)
    text = replace_links(text)
    return text

def heighlight(raw):
    return " [color={}]{}[/color] ".format(Config.HEIGHLIGHT_COLOUR, raw)


# testing function
async def main():
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