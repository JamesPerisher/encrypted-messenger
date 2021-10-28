from app.customwidgets import KVNotifications, KVPOPupSearch, KVPOPupShair
from backend.asyncrun import InputIterator, run
from backend.cache import Cache
from backend.session import Session
from backend.client import Client
from backend.config import Config
from backend.handler import Handler
from backend.shaire import make_code
from backend.signals import Event
from backend.keymanagement import change_info, generate_key, checkpin, decrypt, get_id, get_pub
from app.appmain import AppMain

import os
import asyncio
import json


class Program:
    events = list()
    pageevent = asyncio.Event()
    async def eventloop(self):
        while True:
            if len(self.events) == 0:
                await asyncio.sleep(.5)
                continue
            await self.handle_event(*self.events.pop(0))

    async def event(self, etype, data=""):
        self.events.append((etype, data))

    async def handle_event(self, etype, data=""):
        e = {
            Event.LOGIN         : self.login,
            Event.ADD_FRIEND    : self.empty,
            Event.LOGGED_IN     : self.loggedin,

            Event.AUTH_ERROR    : self.empty,
            Event.NET_ERROR     : self.net_error,
            Event.DISCONNECTED  : self.empty,

            Event.NO_KEY        : self.nokey,
            Event.UNLOCK_PIN    : self.unlockpin,

            Event.SEARCH        : self.search,
            Event.USER_PROPERTY : self.propertypage,
            Event.SHAIRE        : self.shaire
        }[etype]
        return await e(etype, data)

    async def empty(self, etype, data):
        # await self.app.shownotification(KVNotifications, "test")
        print(etype, data)
        return ""

    async def search(self, etype, data):
        await self.app.shownotification(KVPOPupSearch)
    async def shaire(self, etype, data):
        await self.app.shownotification(KVPOPupShair)

    async def propertypage(self, etype, data):
        pass
        # self.app.sm.transition.direction = 'right'
        # self.app.sm.current = "UserPropertyPage"


    async def unlockpin(self, etype, data):
        old = self.app.sm.current

        while True:
            self.app.sm.transition.direction = 'left'
            self.app.sm.current = self.app.PinPage.name

            await self.app.PinPage.setmsg("Enter Pin.")
            await self.pageevent.wait() # gets a pin
            p1 = self.app.PinPage.pin
            self.pageevent.clear()


            if checkpin(self.session.data["privkey"], p1): break

            await self.app.shownotification(KVNotifications, "Pin number incorrect")
            await asyncio.sleep(1)

        self.session.privkey = self.session.data["privkey"]
        self.session.pin = p1
        self.session.data["active"] = True


        cliaccess = json.loads(decrypt(self.session.privkey, get_pub(self.session.privkey), self.session.data["login_token"], p1))

        self.client.jid           = cliaccess["jid"]
        self.client.password      = cliaccess["password"]
        self.client.displayname   = cliaccess["displayname"]
        self.client.displaycolour = cliaccess["displaycolour"]
        
        self.app.sm.transition.direction = 'right'
        self.app.sm.current = old

    async def nokey(self, etype, data):
        old = self.app.sm.current

        while True:
            self.app.sm.transition.direction = 'left'
            self.app.sm.current = self.app.PinPage.name

            await self.app.PinPage.setmsg("Create a pin for quick access.")
            await self.pageevent.wait() # gets a pin
            p1 = self.app.PinPage.pin
            self.pageevent.clear()

            await self.app.PinPage.setmsg("Confirm pin.")
            await self.pageevent.wait() # gets a pin
            p2 = self.app.PinPage.pin
            self.pageevent.clear()

            if p1 == p2: break
            await self.app.shownotification(KVNotifications, "Pin numbers do not match.")

        self.session.privkey = generate_key("NotImplementedError", "NotImplementedError", p1)
        self.session.pin = p1
        self.session.data["active"] = True

        self.app.sm.transition.direction = 'right'
        self.app.sm.current = old

    async def loggedin(self, etype, data):
        self.session.privkey = change_info(self.session.privkey, self.client.displayname, self.client.displaycolour, self.session.pin)

        self.cache   = Cache.from_prog(self) # might be innefficent to have one cache per session but eh

        self.app.sm.transition.direction = 'left'
        self.app.sm.current = self.app.UsersPage.name

        await self.app.UsersPage.update()

        self.session.contactstring = "{}://add-{}-{}".format(Config.APPNAMELINK, self.client.jid, get_id(get_pub(self.session.privkey)))
        im = make_code(self.session.contactstring, userdata_path=Config.USERDATA_DIR)
        im.save(Config.QRCODE_FILE, formats=("png",))

        await self.session.maketoken()
        await self.session.save()

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
        if not os.path.isdir(Config.USERDATA_DIR): os.mkdir(Config.USERDATA_DIR)
        open(Config.SESSION_FILE, "a").close()
        open(Config.CACHE_FILE  , "a").close()

    async def terminal(self):
        async for x in InputIterator(">>> "):
            try:
                print(eval(x))
            except Exception as e:
                try:
                    exec(x)
                except:
                    print(e.__class__.__name__,":", e)

    def asyncstart(self):
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.handle_exception)

        return asyncio.gather(
            self.session.status(), # check stored sessions
            self.app.async_run(async_lib='asyncio'), # run gui
            self.client.start(), # start client manager
            self.eventloop(),
            self.terminal()
            )

    async def save(self):
        pass
        

    def start(self): # make all the objects
        self.make_files()

        self.session = Session.from_prog(self)
        self.client  = Client.from_prog(self)
        self.handler = Handler.from_prog(self)
        self.app     = AppMain.from_prog(self)

        print("made all objects")

        asyncio.get_event_loop().run_until_complete(self.asyncstart())

        print("end")



if __name__ == "__main__":
    Program().start()
