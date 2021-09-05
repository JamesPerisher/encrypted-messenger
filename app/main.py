import asyncio
import logging
import time

from backend.asyncrun import run, AsyncIterator
from backend.backlog import NoNetworkError
from backend.keymanagement import *
from backend.packet import PAC

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.app import App

from kivy.uix.screenmanager import ScreenManager

import app.customwidgets
from app.customwidgets import *

Builder.load_file('app/kvsettings.kv')
Builder.load_file('app/main.kv')
Window.size = (400, 700) # for desktop debug only


class LoginPage(BaseScreen):
    def signup(self):
        if self.children[0].children[7].text.strip() == "":
            self.children[0].children[8].text = "Enter a Username"
        elif not (self.children[0].children[2].children[1].active and self.children[0].children[2].children[3].active):
            self.children[0].children[8].text = "You must agree to all terms and conditions"

        else:
            self.children[0].children[8].text = ""
            self.sm.session["name"] = self.children[0].children[7].text.strip()
            self.sm.session["colour"] = self.children[0].children[4].colour
            self.sm.transition.direction = 'left'
            self.sm.current = "SeedgenPage"

    def on_pre_enter(self):
        self.children[0].children[8].text = ""

    async def login(self):
        self.sm.screens[2].backpg = "LoginPage"
        self.sm.session["_seed"] = None
        self.sm.transition.direction = 'left'
        self.sm.current = "ImportPage"


class UsersPage(BaseScreen1):
    def __init__(self, sm, user=None, **kwargs):
        self.user = user if user else User.from_session(sm, sm.session)
        super().__init__(sm, **kwargs)
        run(self.build())
    
    async def build(self):
        async for i in AsyncIterator(self.sm.session["friends"]):
            data = await self.sm.cm.get_info(i)
            await self.add_user(User(self.sm, data.data[0][1], data.data[0][3], data.data[0][0]))

    async def search(self):
        await self.sm.app.shownotification(KVPOPupSearch(self.sm, Window.width, Window.height))

    async def userproperties(self):
        self.sm.transition.direction = 'right'
        self.sm.current = "UserPropertyPage"

    async def shaire(self):
        await self.sm.app.shownotification(KVPOPupShair(self.sm, Window.width, Window.height))

    async def add_user(self, user):
        self.children[0].children[0].children[0].add_widget(user)


class MessagePage(BaseScreen):
    def __init__(self, sm, meuser, touser, **kwargs):
        self.meuser = meuser
        self.touser = touser # can be (VirtualUser e.g. a group idk how the encryption would work)
        super().__init__(sm, name="MessagePage", **kwargs)

    def key(self, other, keyboard, keycode, display, modifyers):
        _, code = keycode
        if code == "enter" and (not "shift" in modifyers):
            run(self.send())
            return
        other.__class__.keyboard_on_key_down(other, keyboard, keycode, display, modifyers)

    async def clear_messages(self):
        async for i in AsyncIterator(self.children[0].children[1].children[0].children[-1::-1]):
            self.children[0].children[1].children[0].remove_widget(i)

    async def add_message(self, message, time=None): # need to figure out insertion index based on time
        time = int(time.time()) if not time else time
        self.children[0].children[1].children[0].add_widget(Message(message.from_user, message.from_user.username, colour="#00000000", foreground_color=message.colour))
        self.children[0].children[1].children[0].add_widget(message)

    async def relaod(self):
        messages = await self.sm.cm.get_messages_list(self.meuser.userid, self.touser.userid)

        await self.clear_messages()
        async for i in AsyncIterator(messages):
            await self.recieve(i)
            
    async def send(self):
        data = self.children[0].children[0].children[1].text
        ret = await self.sm.cm.msg(self.sm.session["_privkey"], self.meuser.userid, self.touser.userid, data)
        if ret.pactype == PAC.MSGA:
            self.children[0].children[0].children[1].text = ""
            await self.recieve([int(time.time()), get_msg_id(self.meuser.userid, self.touser.userid, ret.data), True])
    
    async def recieve(self, message): # multiuser message group idk fix this later

        if message[2]:
            m = Message(
                self.meuser,
                decrypt(self.sm.session["_privkey"], (await self.sm.cm.get_info(self.meuser.userid)).data[0][2], await self.sm.cm.get_msg(message[1], 1)),
                "", self.meuser.colour
                )
        else:
            m = Message(
                self.touser,
                decrypt(self.sm.session["_privkey"], (await self.sm.cm.get_info(self.touser.userid)).data[0][2], await self.sm.cm.get_msg(message[1], 0)),
                "", self.touser.colour
                )

        await self.add_message(m, message[0])

    async def back(self):
        self.sm.transition.direction = 'right'
        self.sm.current = "UsersPage"

    def update(self, a, b, c):
        a.size[1] = c.size[1]
        b.pos = [0, c.size[1]+10]

    @classmethod
    def from_user(cls, sm, meuser, touser, *args, **kwargs):
        return cls(sm, meuser, touser, *args, **kwargs)
app.customwidgets.MessagePage = MessagePage # do import overwrite

class SeedgenPage(BaseScreen):
    def update(self, other):
        self.seed = generate_seed()
        self.sm.session["_seed"] = self.seed
        other.text = "   ".join(self.sm.session["_seed"])

    def back(self):
        self.sm.transition.direction = 'right'
        self.sm.current = "LoginPage"

    def next(self):
        self.sm.screens[2].backpg = "SeedgenPage"
        self.sm.session["_seed"] = self.seed

        self.sm.transition.direction = 'left'
        self.sm.current = "ImportPage"


class UserPropertyPage(BaseScreen):
    def __init__(self, sm, **kw):
        super().__init__(sm, **kw)
        run(self.build())

    async def logout(self):
        await self.sm.cm.logout()

        self.sm.transition.direction = 'right'
        self.sm.current = "LoginPage"

    async def changeusername(self):
        await self.sm.app.shownotification(KVPOPupChangeName(self.sm, Window.width, Window.height))

    async def changecolour(self):
        await self.sm.app.shownotification(KVPOPupChangeColour(self.sm, Window.width, Window.height))

    async def build(self):
        await self.add_prop(UserPropertySpace())
        await self.add_prop(UserPropertyButton(name="Change username", event=self.changeusername))
        await self.add_prop(UserPropertyButton(name="Change colour", event=self.changecolour))
        await self.add_prop(UserPropertyButton(name="Log out", event=self.logout))

    async def add_prop(self, userproperty):
        self.children[0].children[0].add_widget(userproperty)
    
    async def back(self):
        self.sm.transition.direction = 'left'
        self.sm.current = "UsersPage"


class ImportPage(BaseScreen):
    def back(self): # programaticaly go the last page
        self.sm.transition.direction = 'right'
        self.sm.current = self.backpg

    def on_pre_enter(self, text=""): # error message clearing
        self.children[0].children[5].text = text

    async def auth(self, session):
        self.sm.cm.session = session
        if self.sm.session.get("_seed", None):
            session["_privkey"] = generate_key(session["name"], session["colour"])
            session["id"] = id_from_priv(session["_privkey"])
            session["pubkey"] = get_pub(session["_privkey"])
            await session.cleanup(True) # dump seed from memory
        await session.save()

    async def login (self, session, donote=True):
        await self.auth(session)

        userdata = await self.sm.cm.get_info(session["id"])
        if userdata.data == []:
            if donote:
                Clock.schedule_once(lambda x: self.on_pre_enter("No user for provided seed."), 0) # TODO: proper error notification
            return False
        
        session["id"]     = userdata.data[0][0]
        session["pubkey"] = userdata.data[0][2]
        session["name"], session["colour"] = get_info(session["pubkey"])
        await session.save()

        await self.sm.app.reset_UserPage()
        self.sm.current = "UsersPage"

        return True

    async def signup(self, session):
        await self.auth(session)
        await self.sm.cm.register(session["id"], session["pubkey"])

    async def next(self): # hadle signing/signup page next button
        if self.sm.session.get("_seed", None):
            if not self.sm.session.get("_seed", None) == self.children[0].children[2].text.split():
                self.children[0].children[5].text = "Seed does not match"
                return
            await self.signup(self.sm.session)
        else:
            self.sm.session["_seed"] = self.children[0].children[2].text.split()
        await self.login(self.sm.session)


class Main(App):
    def __init__(self, clientmanager, session, **kwargs):
        self.cm = clientmanager
        self.session = session
        self.session["_privkey"] = self.session["privkey"]
        super().__init__(**kwargs)

    def on_request_close(self, arg): # close asyncio eventloop so program will exit
        logging.warn("Exiting program")
        asyncio.get_event_loop().stop()
        return False

    async def reset_UserPage(self):
        await self.update_images()
        self.sm.remove_widget(self.sm.get_screen("UsersPage"))
        self.sm.add_widget(UsersPage(self.sm, User.from_session(self.sm, self.session), name="UsersPage"))
        self.sm.current = "UsersPage"

    async def shownotification(self, note, msg="msgerr"):
        cc = self.sm.current_screen
        cc.add_widget(note, 0)
        if isinstance(note, KVNotifications):
            note.children[0].children[0].text = msg
        note.anim.start(note.children[0])

        note.anim.bind(on_complete=lambda a,b : cc.remove_widget(note))

    async def update_images(self):
        Cache.remove('kv.image')
        Cache.remove('kv.texture')

    def handle_exception(self, loop, context):
        if isinstance(context.get("exception"), NoNetworkError):
            return run(self.shownotification(KVNotifications(self.sm, Window.width, Window.height), "No network connection."))
        return loop.default_exception_handler(context)

    def build(self): # build all screens
        Window.bind(on_request_close=self.on_request_close)
        self.sm = ScreenManager()
        self.sm.cm = self.cm
        self.sm.session = self.session
        self.sm.app = self
        screens = [
            LoginPage       (self.sm, name="LoginPage"       ),
            SeedgenPage     (self.sm, name="SeedgenPage"     ),
            ImportPage      (self.sm, name="ImportPage"      ),
            UsersPage       (self.sm, name="UsersPage"       ),
            MessagePage     (self.sm, "meuser(err)", "touser(err)"),
            UserPropertyPage(self.sm, name="UserPropertyPage")
        ]

        for i in screens:
            self.sm.add_widget(i)

        self.sm.current = "LoginPage"
        run(screens[2].login(self.session, False))


        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.handle_exception)

        return self.sm
