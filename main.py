import os
import json
import asyncio
import logging

from backend.cache import Cache
from backend.client import Client
from backend.config import Config
from backend.signals import Event
from backend.handler import Handler
from backend.session import Session
from backend.shaire import make_code
from backend.asyncrun import InputIterator, run
from backend.keymanagement import change_info, generate_key, checkpin, decrypt, get_id, get_pub

from app.appmain import AppMain
from app.customwidgets import KVNotifications, KVPOPupSearch, KVPOPupShair


# The main Program object
class Program:
    def __init__(self, debug=False) -> None:
        self.debug = debug # are we debugging
    events = list()
    pageevent = asyncio.Event()
    async def eventloop(self): # handle events in a loop
        while True:
            if len(self.events) == 0:
                await asyncio.sleep(.01)
                continue
            await self.handle_event(*self.events.pop(0))
    # add an event
    async def event(self, etype, data=""):
        self.events.append((etype, data))
    # event handler
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
    # empty handler
    async def empty(self, etype, data):
        return ""
    # handle search request
    async def search(self, etype, data):
        await self.app.shownotification(KVPOPupSearch)
    # handle shaire request
    async def shaire(self, etype, data):
        await self.app.shownotification(KVPOPupShair)
    # handle userproperty page request
    async def propertypage(self, etype, data):
        self.app.sm.transition.direction = 'right'
        self.app.sm.current = self.app.UserPropertyPage.name

    # handle pinumber unlock request
    async def unlockpin(self, etype, data):
        while True:
            self.app.sm.transition.direction = 'left'
            self.app.sm.current = self.app.PinPage.name
            p1 = await self.app.PinPage.get_pin("Enter pin.")

            if checkpin(self.session.data["privkey"], p1): break # we good return
            # error
            await self.app.shownotification(KVNotifications, "Pin number incorrect")
            await asyncio.sleep(1)

        # decrypt data
        self.session.privkey = self.session.data["privkey"]
        self.session.pin = p1
        self.session.data["active"] = True
        
        # decrypt the client key shit
        cliaccess = json.loads(decrypt(self.session.privkey, get_pub(self.session.privkey), self.session.data["login_token"], p1))

        self.client.jid           = cliaccess["jid"]
        self.client.password      = cliaccess["password"]
        self.client.displayname   = cliaccess["displayname"]
        self.client.displaycolour = cliaccess["displaycolour"]

        self.app.sm.transition.direction = 'right'
        self.app.sm.current = self.app.UsersPage.name

    async def nokey(self, etype, data): return # Depricated
    # get user to generate a pin number
    async def generate_pin(self):
        # transfer page
        self.app.sm.transition.direction = 'left'
        self.app.sm.current = self.app.PinPage.name

        # get pin
        while True:
            p1 = await self.app.PinPage.get_pin("Create a pin for quick access.")
            p2 = await self.app.PinPage.get_pin("Confirm pin.")

            if p1 == p2: break
            await self.app.shownotification(KVNotifications, "Pin numbers do not match.")
        return p1

    # logged in event
    async def loggedin(self, etype, data):
        # if we previosuly logged in
        if not self.session.data["active"]:
            self.session.pin = await self.generate_pin()
            self.session.privkey = generate_key(self.client.displayname, self.client.displaycolour, self.session.pin)
            await self.handler.key_change()
        
        # create our cahe
        self.cache   = Cache.from_prog(self) # might be innefficent to have one cache per session
        await self.app.UsersPage.update() # TODO: relocate

        # Spam user with terms and conditions
        self.app.InfoPage.halign = "center"
        with open(Config.TERMS, 'r') as f:
            self.app.InfoPage.data = f.read()

        self.app.InfoPage.data += "\n\n\n"
        self.app.InfoPage.data += "[b]Licence Agreement:[/b]\n"

        with open(Config.LICENCE, 'r') as f:
            self.app.InfoPage.data += f.read()
        self.app.InfoPage.data += "\n\n\n\n\n\n\n\n\n"


        if self.session.data["active"]: return
        self.session.data["active"] = True

        self.app.InfoPage.backpage = self.app.UsersPage.name
        self.app.sm.transition.direction = 'left'
        self.app.sm.current = self.app.InfoPage.name

        # create the rest of the shit they need
        self.session.contactstring = "{}://add-{}-{}".format(Config.APPNAMELINK, self.client.jid, get_id(get_pub(self.session.privkey)))
        im = make_code(self.session.contactstring, userdata_path=Config.USERDATA_DIR)
        im.save(Config.QRCODE_FILE, formats=("png",))

        await self.session.maketoken()
        await self.session.save()

    # show a network error to the user
    async def net_error(self, etype, data):
        await self.app.shownotification(KVNotifications, "Network Error: {}".format(data))
    # go to login
    async def login(self, etype, data):
        self.ignoreevents = True
        await self.app.started.wait()
        self.app.sm.transition.direction = 'left'
        self.app.sm.current = self.app.LoginPage.name
        await asyncio.sleep(0.5)
        self.ignoreevents = False

    # asyncio exceptions get handled in the ether
    def handle_exception(self, loop, context): pass
    # make userdata files
    def make_files(self):
        if not os.path.isdir(Config.USERDATA_DIR): os.mkdir(Config.USERDATA_DIR)
        open(Config.SESSION_FILE, "a").close()
        open(Config.CACHE_FILE  , "a").close()
    # terminal debug for testing
    async def terminal(self):
        if not self.debug: return
        async for x in InputIterator(">>> "):
            try:
                print(eval(x))
            except Exception as e:
                try:
                    exec(x)
                except:
                    print(e.__class__.__name__,":", e)        
    # get all asyncio tasks for the app
    def asyncstart(self):
        loop = asyncio.get_event_loop()
        if self.debug: loop.set_exception_handler(self.handle_exception)
        return asyncio.gather(
            self.session.status(), # check stored sessions
            self.app.async_run(async_lib='asyncio'), # run gui
            self.client.start(), # start client manager
            self.eventloop(),
            self.terminal()
            )

    async def save(self): pass # Depricated
    # close the app
    async def close(self):
        logging.warning("Exiting program")
        asyncio.get_event_loop().stop()
        return False
    # close asyncio eventloop so program will exit
    def on_request_close(self, arg):
        run(self.close())
        
    # start the app
    def start(self): # make all the objects
        self.make_files()

        self.session = Session.from_prog(self)
        self.client  = Client.from_prog(self)
        self.handler = Handler.from_prog(self)
        self.app     = AppMain.from_prog(self)

        print("made all objects")

        asyncio.get_event_loop().run_until_complete(self.asyncstart()) # start mainloop

        print("We ran into a fatal and detremental eror FUCK")

    def debug(self): # debug function (Depricated)
        return


# Start the app if not impoted
if __name__ == "__main__":
    Program(True).start()
