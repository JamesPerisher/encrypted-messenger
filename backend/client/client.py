import asyncio
from asyncio.log import logger
import json
from backend.client.crypto_utils import generate_key, generate_mediator, getid, getmediator, getname, make_id
from backend.p2p.p2p_utils import Address, Id
from backend.p2p.p2p_client import AsyncConnection
from pgpy import PGPKey

from backend.packet import PACKET_TYPE, Packet


class UserInterface:
    def __init__(self, client) -> None:
        self.client = client
    async def none(self): # nothing to do to ui, but is called every time a packet is handled
        pass

    async def get_name(self):
        return input("Name: ")

    async def get_key(self):
        return input("keystring: ")

    async def get_pin(self):
        return input("pin: ")

    async def get_friends(self):
        return [] # TODO: make a commandline input for this idk


class User:
    def __init__(self, id: Id, me, key) -> None:
        self.id = id
        self.me = me
        self.key = key
    def __repr__(self) -> str:
        return f"User({self.id}, <ME>, {self.key})"
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
    def from_string(cls, string: str, me, key=None) -> 'User':
        return cls(Id.from_string(string), me, None)

    def export_dict(self):
        return {
            "id": self.id.get(),
            "key": str(self.key),
        }
    def export_file(self):
        return json.dumps(self.export_dict())

class Client(User):
    def __init__(self, name: str, id: Id, friends: list, key: PGPKey, pin, mediator, ui: UserInterface) -> None:
        super().__init__(id, self, key)
        self.name = name
        self.friends = friends
        self.key = key
        self.pin = pin
        self.mediator = mediator
        self.ui = ui
    def __repr__(self) -> str:
        return f"Client({self.name}, {self.id}, {self.friends}, {self.key}, {self.pin}, {self.mediator}, {self.ui})"

    @classmethod
    def from_dict(cls, data: dict, pin: str, ui):
        self = cls(data['name'], Id(data['id']), [], PGPKey.from_blob(data['key']), pin, Address(data['mediator']['ip'], data['mediator']['port']), ui)
        self.friends = [User.from_string(x, self) for x in data['friends']] # self referential might be dodgy
        return self

    def export_dict(self):
        a = super().export_dict()
        a.update({"friends":[x.export_dict() for x in self.friends]})
        return a


# Used as driver for ui to create a new client before the ui can be assigned a client
# Calles function in ui to get name, key, pin, and friends, then passes off control to the ui(maybe i might change this)
class ClientFactory:
    def __init__(self, ui) -> None:
        self.name     = None
        self.id       = None
        self.key      = None
        self.pin      = None
        self.mediator = None
        self.friends  = None
        self.ui       = ui

    @staticmethod
    def isnone(x): # checks if x is None or ""
        if x == None:
            return True
        if isinstance(x, str):
            return x.strip() == ""
        return False

    async def make(self): # get data and make a client
        while True: # can be jumped to if we need to recheck the data instead of doing recursion
            if self.isnone(self.name):
                self.name = await self.ui.get_name()
                continue

            if self.isnone(self.key):
                try:
                    self.import_key(str(await self.ui.get_key()))
                except ValueError:
                    logger.warning("Invalid key, generating new key")

            if self.isnone(self.id):
                self.id = make_id(self.key)

            if self.isnone(self.pin):
                self.pin = await self.ui.get_pin()
                continue

            if self.isnone(self.mediator) and self.isnone(self.key):
                self.mediator = generate_mediator()

            if self.isnone(self.mediator):
                self.mediator = getmediator(self.key)

            if self.isnone(self.friends):
                self.friends = await self.ui.get_friends()
                continue
            
            if self.isnone(self.key):
                self.key = generate_key(self.name, self.id, self.mediator, self.pin)

            break

        return Client(self.name, self.id, self.friends, self.key, self.pin, self.mediator, self.ui)

    # imports all data in the key
    def import_key(self, key):
        self.key = PGPKey.from_blob(key)
        # data embaeded in the key
        self.id       = getid(self.key)
        self.name     = getname(self.key)
        self.mediator = getmediator(self.key)

    # imports all data in the file
    def import_file(self, file):
        with open(file, "r") as f:
            data = json.loads(f.read())

        # raw data in the file
        self.key      = data.get("key", None)
        self.pin      = None # pin must always be fetched form the user on startup
        self.friends  = data.get("friends", None)

        self.import_key(self.key)



def main():
    ui = UserInterface(None)
    cf = ClientFactory(ui)

    client = asyncio.run(cf.make()) # async handle so ui can function
    ui.client = client # becouase loop of reference bad idea but is neetest method so far
    # print(client)
    print(client.export_file())