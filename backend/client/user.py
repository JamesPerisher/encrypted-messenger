import json
from backend.client.crypto_utils import getid, getmediator, getname
from backend.p2p.p2p_utils import Id
from backend.p2p.p2p_client import AsyncConnection
from pgpy import PGPKey
from backend.packet import PACKET_TYPE, Packet


class User:
    def __init__(self, id: Id, name: str, mediator, key, me) -> None:
        self.id = id
        self.name = name
        self.mediator = mediator
        self.key = key
        self.me = me

    def __repr__(self) -> str:
        return f"User({self.id}, {self.name}, <KEY>, <ME>)"
    def __hash__(self) -> int:
        return self.id.__hash__()
    def __eq__(self, other: object) -> bool:
        return self.id == other.id
    def __ne__(self, other: object) -> bool:
        return self.id != other.id

    async def ping(self, pac, conn): # pong
        await conn.send(Packet(PACKET_TYPE.PING, "PONG!!!"))
        await self.me.ui.none()

    async def handle(self): # to be called each time we want to sync data #TODO: implement lock
        # handles all incoming packets
        conn = AsyncConnection.from_id(self.me.id, self.id, self.sme.mediator)
        while conn.object.keepalive:
            pac = await conn.recv() # get the next packet from the connection

            await { # python switch statement dodgyness
                PACKET_TYPE.PING: self.ping,
            }[pac.type](pac, conn)

    @classmethod
    def from_key(cls, key: PGPKey, me):
        id = getid(key)
        name = getname(key)
        mediator = getmediator(key)
        return cls(id, name, mediator, key, me)
        

    def export_dict(self):
        return {
            "key": str(self.key)
        }
    def export_file(self):
        return json.dumps(self.export_dict())