from backend.signals import PAC, Packet, Event
from backend.basics import BaseObject


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

    async def recv_msg(self, fromjid, data):
        pass

