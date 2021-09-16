import asyncio

from globalconfig import APPNAMELINK, NEWWORD_A, NEWWORD_B, NEWWORD_FULL, HEIGHLIGHT_COLOUR


class Renderer:
    def __init__(self, cm) -> None:
        self.cm = cm # reference to client manager

    # render controill charecters prevent xxs style attacks
    async def render_controls(self, value):
        return value.replace("[", "&bl;").replace("]", "&br;").replace("&", "&amp;")

    # render links and references to a pre render format
    async def render_text_refs(self, text):
        # making a word for each renderable ref type
        _tmp = text\
            .replace("http://"   .format(           ), "{}http://"   .format(NEWWORD_FULL             ))\
            .replace("https://"  .format(           ), "{}https://"  .format(NEWWORD_FULL             ))\
            .replace("{}://user_".format(APPNAMELINK), "{}{}://user_".format(NEWWORD_FULL, APPNAMELINK))\
            .replace("{}://msg_" .format(APPNAMELINK), "{}{}://msg_" .format(NEWWORD_FULL, APPNAMELINK))\
            .split(NEWWORD_A)

        # find the endes of a word and split it
        words = list()
        for x in _tmp:
            if x.startswith(NEWWORD_B):
                x += " "
                w1, w2 = x.split(" ", 1)
                words.append(w1[len(NEWWORD_B)::])
                words.append(w2)
                continue
            words.append(x)
        
        output = list()
        for i in words:
            if (i.split("://")[0]=="http" and i!="http") or (i.split("://")[0]=="https" and i!="https"):# http and https rendering
                output.append(
                    "[ref={}]{}[/ref]".format(
                    i,
                    await self.url_function(i)
                    )
                )
                
            elif i.split("_")[0]=="{}://user".format(APPNAMELINK): # user rendering
                output.append(
                    "[ref={}]{}[/ref]".format(
                    i,
                    await self.user_function(self.get_id(i))
                    )
                )
                
            elif i.split("_")[0]=="{}://msg".format(APPNAMELINK):# msg rendering
                output.append(
                    "[ref={}]{}[/ref]".format(
                    i,
                    await self.msg_function(self.get_id(i))
                    )
                )
            else:
                output.append(i)
        return "".join(output)

    # extract id from string
    def get_id(self, raw):
        return raw.split("://", 1)[-1]

    def heighlight(self, raw):
        return " [color={}]{}[/color] ".format(HEIGHLIGHT_COLOUR, raw)

    # get nice render info from database
    async def user_function(self, id):
        return self.heighlight("NAME({})".format(id))

    async def url_function(self, id):
        return self.heighlight("{}".format(id))

    async def msg_function(self, id):
        return self.heighlight("MSG({})".format(id))


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