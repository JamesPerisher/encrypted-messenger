from backend.asyncrun import AsyncIterator
from backend.signals import PAC, Packet, Event
from backend.basics import BaseObject
from backend.keymanagement import decrypt, get_info, get_pub
from backend.textrenderer import get_user_line, render_text
import asyncio

class Handler(BaseObject):
    def __init__(self, prog) -> None:
        super().__init__(prog)
        self.prog.client.msgevent = self.recv_msg # handle incoming messages

    async def key_change(self):
        async for i in AsyncIterator(await self.prog.client.get_contacts()): # gets contacts from cloud
            await self.request_pug(i, Packet(PAC.GET_PUB))
    
    def send(self, to_jid, p, raw="Hidden..."):
        ret = self.prog.client.send(to_jid, p)
        if to_jid == self.prog.client.jid: return ret # dont self render messages to urself
        
        return asyncio.gather(ret, self.recived_msg(to_jid, Packet(PAC.INTERNAL, raw)))


    async def get_key(self, jid):
        self.prog.cache.get(Packet(PAC.PUB_KEY, jid), self.prog.event(Event.ADD_FRIEND, jid))

    def recv_msg(self, fromjid, p):
        fromjid = str(fromjid).split("/")[0]
        return {
            PAC.SEND_MSG: self.recived_msg,
            PAC.GET_PUB : self.request_pug,
            PAC.SEND_PUB: self.recived_pub,
        }[p.pactype](fromjid, p)

    async def request_pug(self, fromjid, pack):
        await self.prog.client.send(fromjid, Packet(PAC.SEND_PUB, get_pub(self.prog.session.privkey)))

    async def recived_pub(self, fromjid, p):
        self.prog.session.data["friends"][fromjid] = p.data
        await self.prog.session.save()

        user = self.prog.app.UsersPage.userlist[fromjid]

        user.username, user.colour = get_info(p.data)
        await self.recived_msg(fromjid, Packet(PAC.INTERNAL, "{} has a different encryption key (It is possible that this is not {})".format(fromjid, fromjid)))
        await self.prog.app.UsersPage.update()

    async def recived_msg(self, fromjid, p):
        userline = ""

        if p.pactype == PAC.INTERNAL:
            message = p.data
        else:
            if not self.prog.cache.get("{}_last".format(fromjid), None) == fromjid:
                userline = get_user_line(self.prog, self.prog.session.data["friends"].get(fromjid, self.prog.session.data["friends"]["empty"]))
            self.prog.cache["{}_last".format(fromjid)] = fromjid

            message = decrypt(
                    self.prog.session.privkey,
                    await self.prog.session.get_key(fromjid),
                    p.data,
                    self.prog.session.pin
                )

        self.prog.cache[fromjid] += "\n{}{}".format(
            userline ,
            await render_text(message)
        )
        
        name = "MessagePage-{}".format(fromjid)
        if not name in self.prog.app.sm.screen_names: return # ignore unknown messages
        await self.prog.app.sm.get_screen(name).reload()
