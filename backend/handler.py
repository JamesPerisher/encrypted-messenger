import asyncio

from kivy.cache import Cache

from backend.basics import BaseObject
from backend.asyncrun import AsyncIterator
from backend.signals import PAC, Packet, Event
from backend.textrenderer import get_user_line, render_text
from backend.keymanagement import decrypt, get_info, get_pub


# handle all incoming and outgoing messages
class Handler(BaseObject):
    def __init__(self, prog) -> None:
        super().__init__(prog)
        self.prog.client.msgevent = self.recv_msg # handle incoming messages

    # deal with a key changing somewhere and update ALLLLLLL the relevant things
    async def key_change(self):
        self.prog.session.data["privkey"] = self.prog.session.privkey
        self.prog.session.data["pubkey"] = get_pub(self.prog.session.data["privkey"])
        self.prog.client.displayname, self.prog.client.displaycolour = get_info(self.prog.session.data["pubkey"])
        self.prog.session.data["friends"][self.prog.client.jid] = self.prog.session.data["pubkey"]

        await self.prog.session.maketoken()
        await self.prog.session.save()

        async for i in AsyncIterator(await self.prog.client.get_contacts()): # gets contacts from cloud
            await self.request_pug(i, Packet(PAC.GET_PUB))
        
        # redraw profile images
        Cache.remove('kv.image')
        Cache.remove('kv.texture')

    # send a message
    def send(self, to_jid, p, raw="Hidden..."):
        ret = self.prog.client.send(to_jid, p)
        if to_jid == self.prog.client.jid: return ret # dont self render messages to urself
        
        return asyncio.gather(ret, self.recived_msg(to_jid, Packet(PAC.ME, raw)))

    # get a key from a different user
    async def get_key(self, jid):
        self.prog.cache.get(Packet(PAC.PUB_KEY, jid), self.prog.event(Event.ADD_FRIEND, jid))

    # message recived event
    def recv_msg(self, fromjid, p):
        fromjid = str(fromjid).split("/")[0]
        return {
            PAC.SEND_MSG: self.recived_msg,
            PAC.GET_PUB : self.request_pug,
            PAC.SEND_PUB: self.recived_pub,
        }[p.pactype](fromjid, p)

    # send someone my public key the asked for
    async def request_pug(self, fromjid, pack):
        await self.prog.client.send(fromjid, Packet(PAC.SEND_PUB, get_pub(self.prog.session.privkey)))

    # i got someones public key
    async def recived_pub(self, fromjid, p):
        self.prog.session.data["friends"][fromjid] = p.data
        await self.prog.session.save()

        user = self.prog.app.UsersPage.userlist[fromjid]

        user.username, user.colour = get_info(p.data)
        # notify user they public key for fromjid has changed
        await self.recived_msg(fromjid, Packet(PAC.INTERNAL, "{} has a different encryption key (Verify that {} is who they claim to be)".format(fromjid, fromjid)))
        await self.prog.app.UsersPage.update()

    async def recived_msg(self, fromjid, p):
        # userline part of the current line
        userline = ""

        # use self.prog.cache["{}_last".format(fromjid)] stores the last message sender
        old = self.prog.cache.get("{}_last".format(fromjid), None)      # the previouse messager
        new = self.prog.client.jid if p.pactype == PAC.ME else fromjid  # the current messager

        if old == None:
            userline = "This is the beggining of your conversation with {}. \n".format(await render_text(fromjid))
        else:
            if old == new:
                userline = ""
            else:
                userline = get_user_line(self.prog.session.data["friends"].get(new, self.prog.session.data["friends"]["empty"]))

        self.prog.cache["{}_last".format(fromjid)] = new

        # ^^ is just to determine if we need a new userline or if the same person double messaged


        # message part of the current line
        if p.pactype == PAC.ME:
            message = p.data
        else:
            message = decrypt(
                    self.prog.session.privkey,
                    await self.prog.session.get_key(fromjid),
                    p.data,
                    self.prog.session.pin
                )

        # render lines to page
        self.prog.cache[fromjid] += "{}{}\n".format(userline, await render_text(message))
        
        name = "MessagePage-{}".format(fromjid)
        if not name in self.prog.app.sm.screen_names: return # ignore unknown messages
        await self.prog.app.sm.get_screen(name).reload()
