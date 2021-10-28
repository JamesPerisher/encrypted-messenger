import asyncio
import re
from config import Config


class Renderer:
    # replace charecter
    def replace_charecters(self, text):
        text = text.replace("&bl;", "[").replace("&br;", "]").replace("&amp;", "&")
        return text

    # find all jid addreesses in a string
    def find_jids(self, text):
        jids = []
        for match in re.finditer(r'[\w\.-]+@[\w\.-]+', text):
            jids.append(match.group(0))
        return jids

    # replace all jid addresses with a link
    def replace_jids(self, text):
        for jid in self.find_jids(text):
            text = text.replace(jid, "[ref={}]{}[/ref]".format(jid, self.heighlight(jid)))
        return text


    # find all links in text
    def find_links(self, text):
        links = []
        for match in re.finditer(r'(https?://[^\s]+)', text):
            links.append(match.group(0))
        return links

    #replace all links with a link
    def replace_links(self, text):
        for link in self.find_links(text):
            text = text.replace(link, "[ref={}]{}[/ref]".format(link, self.heighlight(link)))
        return text

    # render links and references to a pre render format
    async def render_text_refs(self, text):
        text = self.replace_charecters(text)
        text = self.replace_jids(text)
        text = self.replace_links(text)
        return text

    def heighlight(self, raw):
        return " [color={}]{}[/color] ".format(Config.HEIGHLIGHT_COLOUR, raw)


# testing function
async def main():
    r = Renderer(None)
    print(await r.render_text_refs("some text http://url.idk somemore text mabaybe http://another maybe more idk and replaces"))
    print(await r.render_text_refs("some text https://url.idk somemore text mabaybe https://another maybe more idk and replaces"))
    print(await r.render_text_refs("some text encrypted-msger://user_wquf8uewgf more message"))
    print(await r.render_text_refs("some text encrypted-msger://msg_helo9825972398    more medssage"))
    print(await r.render_text_refs("some text bob://msg_helo9825972398 more medssage"))
    print("    ")
    print(await r.render_text_refs("some texthttp://url.idk somemore text mabaybe http://another maybe more idk and replaces"))
    print(await r.render_text_refs("some texthttps://url.idk somemore text mabaybe https://another maybe more idk and replaces"))
    print(await r.render_text_refs("some textencrypted-msger://user_wquf8uewgf more message"))
    print(await r.render_text_refs("some textencrypted-msger://msg_helo9825972398    more medssage"))
    print(await r.render_text_refs("some textbob://msg_helo9825972398 more medssage"))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())