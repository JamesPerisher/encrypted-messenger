from backend.signals import PAC, Packet, Event
from backend.basics import BaseObject
from backend.keymanagement import decrypt, get_info, get_pub
from backend.textrenderer import get_user_line, render_text
import asyncio

class Handler(BaseObject):
    def __init__(self, prog) -> None:
        super().__init__(prog)
        self.prog.client.msgevent = self.recv_msg # handle incoming messages
    
    def send(self, to_jid, p):
        ret = self.prog.client.send(to_jid, p)
        if to_jid == self.prog.client.jid: return ret # dont self render messages to urself
        
        return asyncio.gather(ret, self.recv_msg(to_jid, p))


    async def get_key(self, jid):
        self.prog.cache.get(Packet(PAC.PUB_KEY, jid), self.prog.event(Event.ADD_FRIEND, jid))

    def recv_msg(self, fromjid, p):
        # data = data.split("::")[1]
        fromjid = str(fromjid).split("/")[0]
        return {
            PAC.SEND_MSG: self.send_msg,
            PAC.GET_PUB : self.getpubkey,
            PAC.SEND_PUB: self.send_pub,
        }[p.pactype](fromjid, p)

    async def getpubkey(self, fromjid, pack):
        await self.prog.client.send(fromjid, Packet(PAC.SEND_PUB, get_pub(self.prog.session.privkey)))

    async def send_pub(self, fromjid, p):
        # if await self.prog.session.get_key(self.prog.client.jid, False): return
        self.prog.session.data["friends"][fromjid] = p.data
        await self.prog.session.save()

        user = self.prog.app.UsersPage.userlist[fromjid]

        user.username, user.colour = get_info(p.data)
        await self.prog.app.UsersPage.update()

    async def send_msg(self, fromjid, p):
        userline = ""
        if not self.prog.cache.get("{}_last".format(fromjid), None) == fromjid:
            userline = get_user_line(self.prog, self.prog.session.data["friends"].get(fromjid, self.prog.session.data["friends"]["empty"]))
        self.prog.cache["{}_last".format(fromjid)] = fromjid

    
        self.prog.cache[fromjid] += "\n{}{}".format(
            userline ,
            await render_text(decrypt(
                self.prog.session.privkey,
                await self.prog.session.get_key(fromjid),
                p.data,
                self.prog.session.pin
            ))
        )
        
        name = "MessagePage-{}".format(fromjid)
        if not name in self.prog.app.sm.screen_names: return # ignore unknown messages
        await self.prog.app.sm.get_screen(name).reload()
