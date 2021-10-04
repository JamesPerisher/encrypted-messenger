from backend.cache import Cache
from backend.client import XMPPClient
from backend.config import Config
from backend.cryptomanager import CryptoManager
from backend.handler import Handler
from backend.signals import Event

import os
import asyncio

def run(coroutine): # insert event into the event loop
    return asyncio.get_event_loop().create_task(coroutine)

class Program:
    async def empty(self, etype, data):
        print(etype, data)
        return ""
    async def event(self, etype, data=""): # event handler
        e = {
            Event.ERROR      : self.empty(etype, data),
            Event.ADD_FRIEND : self.empty(etype, data)
        }[etype]

        return await e(etype, data)

    def make_files(self):
        if not os.path.isdir(self.config.USERDATA_DIR): os.mkdir(self.config.USERDATA_DIR)
        open(self.config.CACHE_FILE, "a").close()
        open(self.config.XMPPDATA_FILE, "a").close()
        open(self.config.PRIV_KEY, "a").close()
        

    def start(self): # make all the objects
        # thread 1
        self.config  = Config.from_prog(self)
        self.make_files()

        self.cache   = Cache.from_prog(self)
        self.crypto  = CryptoManager.from_prog(self)
        self.client = XMPPClient.from_prog(self)
        self.handler = Handler.from_prog(self)

        print("made all objects")

        self.client.start()



if __name__ == "__main__":
    prog = Program()
    prog.start()