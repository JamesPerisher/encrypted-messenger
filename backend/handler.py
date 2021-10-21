from backend.signals import PAC, Packet, Event
from backend.basics import BaseObject
from backend.keymanagement import get_info, get_pub

class Handler(BaseObject):
    def __init__(self, prog) -> None:
        super().__init__(prog)
        self.prog.client.msgevent = self.recv_msg # handle incoming messages

    async def get_key(self, jid):
        self.prog.cache.get(Packet(PAC.PUB_KEY, jid), self.prog.event(Event.ADD_FRIEND, jid))

    async def send_msg(self, tojid, data):
        pubkey = await self.get_key(tojid)
        msg = await self.prog.crypto.encypt(pubkey, data)

        return await self.prog.client.send(tojid, msg)


    def recv_msg(self, fromjid, data):
        fromjid = str(fromjid).split("/")[0]
        p = Packet.from_raw(data)
        return {
            PAC.GET_PUB: self.getpubkey,
            PAC.SEND_PUB: self.send_pub,
        }[p.pactype](fromjid, p)

    async def getpubkey(self, fromjid, pack):
        await self.prog.client.send(fromjid, Packet(PAC.SEND_PUB, get_pub(self.prog.session.privkey)))

    async def send_pub(self, fromjid, p):
        if await self.prog.session.get_key(self.prog.client.jid, False): return
        self.prog.session.data["friends"][fromjid] = p.data
        await self.prog.session.save()

        try:
            user = self.prog.app.UsersPage.userlist[fromjid]
        except KeyError:
            return

        user.username, user.colour = get_info(p.data)
        await self.prog.app.UsersPage.update()

