import asyncio
from asyncio.log import logger
import json
from backend.client.crypto_utils import generate_key, generate_mediator, getid, getmediator, getname, key_import, make_id
from backend.p2p.p2p_utils import Id
from pgpy import PGPKey
from backend.client.interface import UserInterface
from backend.client.user import User

class Client(User): # should not be directly instantiated but instead through ClientFactory
    def __init__(self, name: str, id: Id, friends: list, key: PGPKey, pin, mediator, ui: UserInterface) -> None:
        super().__init__(id, name, mediator, key, self)
        self.friends = friends
        self.pin = pin
        self.ui = ui
    def __repr__(self) -> str:
        return f"Client({self.name}, {self.id}, {self.friends}, {self.key}, {self.pin}, {self.mediator}, {self.ui})"

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

    async def make_key(self):
        while True:
            if self.isnone(self.name):
                self.name = await self.ui.get_name()
                continue

            if self.isnone(self.id):
                self.id = make_id(self.key)

            if self.isnone(self.pin):
                self.pin = await self.ui.get_pin()
                continue

            if self.isnone(self.mediator):
                self.mediator = generate_mediator()
                continue
            
            # make key now we have the data
            self.key = generate_key(self.name, self.id, self.mediator, self.pin)

            break

    async def make(self): # get data and make a client
        while True: # can be jumped to if we need to recheck the data instead of doing recursion
            if self.isnone(self.key):
                if not self.import_key(await self.ui.get_key("User")):
                    if await self.ui.is_do_thing("Make key"):
                        await self.make_key()
                    else:
                        continue

            if self.isnone(self.friends):
                self.friends = await self.ui.get_friends()
                continue
            
            break

        return Client(self.name, self.id, self.friends, self.key, self.pin, self.mediator, self.ui)

    # imports all data in the key
    def import_key(self, key: PGPKey):
        self.key = key
        # data embaeded in the key
        self.id       = getid(self.key)
        self.name     = getname(self.key)
        self.mediator = getmediator(self.key)
        return key

    # imports all data in the file
    def import_file(self, file):
        with open(file, "r") as f:
            data = json.loads(f.read())

        # raw data in the file
        self.pin      = None # pin must always be fetched form the user on startup
        self.friends  = data.get("friends", None)

        k = key_import(data.get("key", None)) # imports key if possible
        if k:
            self.import_key(k)


async def startclient(ui: UserInterface): # makes client then passes control to the ui
    # make client
    factory = ClientFactory(ui)
    client = await factory.make()
    ui.client = client

    await ui.actionloop()


def main():
    asyncio.run(startclient(UserInterface(None)))