from json import loads
from app.customwidgets import KVNotifications
from backend.session import Session
from backend.client import Client
from backend.config import Config
from backend.cryptomanager import CryptoManager
from backend.handler import Handler
from backend.signals import Event
from app.appmain import AppMain

import os
import asyncio

from backend.asyncrun import run

class Program:
    ignoreevents = False
    async def event(self, etype, data=""): # event handler syncronouse handling
        if self.ignoreevents: return
        e = {
            Event.LOGIN       : self.login,
            Event.ADD_FRIEND  : self.empty,
            Event.LOGGED_IN   : self.loggedin,

            Event.AUTH_ERROR  : self.empty,
            Event.NET_ERROR   : self.net_error,
            Event.DISCONNECTED: self.empty
        }[etype]
        return await e(etype, data)

    async def empty(self, etype, data):
        # await self.app.shownotification(KVNotifications, "test")
        print(etype, data)
        return ""

    async def loggedin(self, etype, data):
        self.app.sm.transition.direction = 'left'
        self.app.sm.current = self.app.UsersPage.name

        await self.session.save(await self.session.maketoken())

    async def net_error(self, etype, data):
        await self.app.shownotification(KVNotifications, "Network Error: {}".format(data))

    async def login(self, etype, data):
        self.ignoreevents = True
        await self.app.started.wait()
        self.app.sm.transition.direction = 'left'
        self.app.sm.current = self.app.LoginPage.name
        await asyncio.sleep(0.5)
        self.ignoreevents = False


    def handle_exception(self, loop, context):
        pass

    def make_files(self):
        if not os.path.isdir(self.config.USERDATA_DIR): os.mkdir(self.config.USERDATA_DIR)
        open(self.config.CACHE_FILE, "a").close()
        open(self.config.XMPPDATA_FILE, "a").close()
        open(self.config.PRIV_KEY, "a").close()

    def asyncstart(self):
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.handle_exception)

        return asyncio.gather(
            self.session.status(), # check stored sessions
            self.app.async_run(async_lib='asyncio'), # run gui
            self.client.start() # start client manager
            )

    async def save(self):
        pass
        

    def start(self): # make all the objects
        self.config  = Config.from_prog(self)
        self.make_files()

        self.session = Session.from_prog(self)
        self.crypto  = CryptoManager.from_prog(self)
        self.client  = Client.from_prog(self)
        self.handler = Handler.from_prog(self)
        self.app     = AppMain.from_prog(self)

        print("made all objects")

        asyncio.get_event_loop().run_until_complete(self.asyncstart())

        print("end")



if __name__ == "__main__":
    Program().start()
