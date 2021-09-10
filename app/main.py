import asyncio
import logging
import time

from backend.asyncrun import run, AsyncIterator
from backend.handler import NoNetworkError
from backend.keymanagement import *
from backend.packet import PAC, Packet

from app.shaire import make_code
from app.messagelist import Message, MessageList

from kivy.utils import get_color_from_hex
from kivy.graphics import Line, Color
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
    async def signup(self):
        if self.children[0].children[8].text.strip() == "":
            await self.app.shownotification(KVNotifications(self, Window.width, Window.height), "No username.")
        elif not (self.children[0].children[3].children[1].active and self.children[0].children[3].children[3].active):
            await self.app.shownotification(KVNotifications(self, Window.width, Window.height), "You must agree to all terms and conditions.")

        else:
            self.app.session["name"] = self.children[0].children[8].text.strip()
            self.app.session["colour"] = self.children[0].children[5].colour
            self.app.sm.transition.direction = 'left'
            self.app.sm.current = "SeedgenPage"

    async def login(self):
        self.app.sm.get_screen("ImportPage").backpg = "LoginPage"
        self.app.session["_seed"] = None
        self.app.sm.transition.direction = 'left'
        self.app.sm.current = "ImportPage"


class UsersPage(BaseScreen1):
    def __init__(self, app, user=None, **kwargs):
        self.user = user if user else User.from_session(app, app.session)
        super().__init__(app, **kwargs)
        run(self.build())
    
    async def build(self):
        make_code("encrypted-msger://user_{}".format(self.app.session["id"])).save("userdata/shaire.png")

        async for i in AsyncIterator(self.app.session["friends"]):
            data = await self.app.cm.get_info(i)
            await self.add_user(User(self.app, data.data[0][1], data.data[0][3], data.data[0][0]))

    async def search(self):
        await self.app.shownotification(KVPOPupSearch(self.app, Window.width, Window.height))

    async def userproperties(self):
        self.app.sm.transition.direction = 'right'
        self.app.sm.current = "UserPropertyPage"

    async def shaire(self):
        await self.app.shownotification(KVPOPupShair(self.app, Window.width, Window.height))

    async def add_user(self, user):
        self.children[0].children[0].children[0].add_widget(user)


class MessagePage(BaseScreen):
    def __init__(self, app, meuser, touser, **kwargs):
        super().__init__(app, **kwargs)
        self.meuser = meuser
        self.touser = touser # can be (VirtualUser e.g. a group idk how the encryption would work)
        run(self.make())

    async def make(self): # load cached messages
        data = await self.app.cm.cache.get(Packet(PAC.NAN, self.touser.userid))
        self.list = MessageList.jimport(data if data else {"data":{}, "next":-1}, self.app.session["_privkey"])
        self.app.cm.cache.data[Packet(PAC.NAN, self.touser.userid)] = self.list
        await self.app.cm.cache.save()
        await self.reload()

    def key(self, other, keyboard, keycode, display, modifyers):
        _, code = keycode
        if code == "enter" and (not "shift" in modifyers):
            run(self.send())
            return
        other.__class__.keyboard_on_key_down(other, keyboard, keycode, display, modifyers)


    async def reload(self):
        retime = self.app.session["friends"][self.touser.userid]
        await self.app.cm.cache.save()
        await self.app.session.save()
        self.app.session["friends"][self.touser.userid] = int(time.time())
        messages = await self.app.cm.get_messages_list(self.meuser.userid, self.touser.userid, retime)

        async for i in AsyncIterator(messages):
            await self.recieve(i)
        await self.refresh()
            
    async def send(self):
        data = self.children[0].children[0].children[1].text
        if data.strip() == "": return
        ret = await self.app.cm.msg(self.app.session["_privkey"], self.meuser.userid, self.touser.userid, data)
        if ret.pactype == PAC.MSGA:
            self.children[0].children[0].children[1].text = ""
            await self.recieve([int(time.time()), get_msg_id(self.meuser.userid, self.touser.userid, ret.data), True]) # tell recieve we just sent a message
            await self.refresh()

    async def draw_displacement(self, obj):
        anchors = self.children[0].children[1].children[0].anchors
        lineset = anchors[str(len(anchors)-1)][1] - anchors[str(len(anchors)-2)][1] # distance between a line

        with obj.canvas:
            for key in range(len(anchors)-2):
                Color(*get_color_from_hex(self.colourtable[key]))
                a = obj.height-anchors[str(key)][1] - lineset
                b = obj.height-anchors[str(key+1)][1]
                Line(points=[10, a, 10, b], width=1)
                # # debug
                # Line(points=[0, a, 20, a], width=1)
                # Line(points=[0, b, 20, b], width=1)
        obj.text = ("\n".join(obj.text.split("\n")[0:-2])) + "\n\n"

    
    async def refresh(self):
        self.colourtable, self.children[0].children[1].children[0].text = await self.list.export()
        Clock.schedule_once(lambda x: run(self.draw_displacement(self.children[0].children[1].children[0])), 0) # draw sidebar color thingy

    async def recieve(self, message): # multiuser message group idk fix this later
        
        if message[2]: # do i get the data encoded by foregn key (when from someone is me)
            data = decrypt(self.app.session["_privkey"], (await self.app.cm.get_info(self.meuser.userid)).data[0][2], await self.app.cm.get_msg(message[1], 1))
            fromuser = self.meuser
        else:
            data = decrypt(self.app.session["_privkey"], (await self.app.cm.get_info(self.touser.userid)).data[0][2], await self.app.cm.get_msg(message[1], 0))
            fromuser = self.touser

        m = Message.from_bits(message[0], data, message[1], fromuser.username, fromuser.colour)
        await self.list.add_message(m.data)



    async def back(self):
        self.app.sm.transition.direction = 'right'
        self.app.sm.current = "UsersPage"

    def update(self, a, b, c):
        a.size[1] = c.size[1]
        b.pos = [0, c.size[1]+10]

    @classmethod
    def from_user(cls, app, meuser, touser, *args, **kwargs):
        return cls(app, meuser, touser, *args, **kwargs)
app.customwidgets.MessagePage = MessagePage # do import overwrite

class SeedgenPage(BaseScreen):
    def update(self, other):
        self.seed = generate_seed()
        self.app.session["_seed"] = self.seed
        other.text = "   ".join(self.app.session["_seed"])

    def back(self):
        self.app.sm.transition.direction = 'right'
        self.app.sm.current = "LoginPage"

    def next(self):
        self.app.sm.get_screen("ImportPage").backpg = "SeedgenPage"
        self.app.session["_seed"] = self.seed

        self.app.sm.transition.direction = 'left'
        self.app.sm.current = "ImportPage"


class UserPropertyPage(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        run(self.build())

    async def logout(self):
        await self.app.cm.logout()

        self.app.sm.transition.direction = 'right'
        self.app.sm.current = "LoginPage"

    async def changeusername(self):
        await self.app.shownotification(KVPOPupChangeName(self.app, Window.width, Window.height))

    async def changecolour(self):
        await self.app.shownotification(KVPOPupChangeColour(self.app, Window.width, Window.height))

    async def build(self):
        await self.add_prop(UserPropertySpace())
        await self.add_prop(UserPropertyButton(name="Change username", event=self.changeusername))
        await self.add_prop(UserPropertyButton(name="Change colour", event=self.changecolour))
        await self.add_prop(UserPropertyButton(name="Log out", event=self.logout))

    async def add_prop(self, userproperty):
        self.children[0].children[0].add_widget(userproperty)
    
    async def back(self):
        self.app.sm.transition.direction = 'left'
        self.app.sm.current = "UsersPage"


class ImportPage(BaseScreen):
    def back(self): # programaticaly go the last page
        self.app.sm.transition.direction = 'right'
        self.app.sm.current = self.backpg

    def on_pre_enter(self):
        self.children[0].children[2].text = "" # clear seed input box

    async def auth(self, session):
        self.app.cm.session = session
        if self.app.session.get("_seed", None):
            session["_privkey"] = generate_key(session["name"], session["colour"])
            session["id"] = id_from_priv(session["_privkey"])
            session["pubkey"] = get_pub(session["_privkey"])
            await session.update()
            await session.cleanup(True) # dump seed from memory
            session["_privkey"] = session["privkey"]
        await session.save()

    async def login (self, session, donote=True):
        await self.auth(session)

        userdata = await self.app.cm.get_info(session["id"])
        if userdata.data == []:
            if donote:
                await self.app.shownotification(KVNotifications(self.app, Window.width, Window.height), "No user for provided seed.")
            return False
        
        session["id"]     = userdata.data[0][0]
        session["pubkey"] = userdata.data[0][2]
        session["name"], session["colour"] = get_info(session["pubkey"])
        await session.save()

        await self.app.reset_UserPage()
        self.app.sm.current = "UsersPage"

        return True

    async def signup(self, session):
        await self.auth(session)
        await self.app.cm.register(session["id"], session["pubkey"])

    async def next(self): # hadle signing/signup page next button
        if self.app.session.get("_seed", None):
            if not self.app.session.get("_seed", None) == self.children[0].children[2].text.split():
                self.children[0].children[5].text = "Seed does not match"
                return
            await self.signup(self.app.session)
        else:
            self.app.session["_seed"] = self.children[0].children[2].text.split()
        await self.login(self.app.session)


class Main(App):
    def __init__(self, clientmanager, session, **kwargs):
        self.cm = clientmanager
        self.session = session
        self.session["_privkey"] = self.session["privkey"]
        super().__init__(**kwargs)

    async def close(self):
        await self.cm.cache.save()
        logging.warn("Exiting program")
        asyncio.get_event_loop().stop()
        return False

    def on_request_close(self, arg): # close asyncio eventloop so program will exit
        run(self.close())

    async def reset_UserPage(self):
        await self.update_images()
        self.sm.remove_widget(self.sm.get_screen("UsersPage"))
        self.sm.add_widget(UsersPage(self, User.from_session(self, self.session), name="UsersPage"))
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
            return run(self.shownotification(KVNotifications(self, Window.width, Window.height), "No network connection."))
        return loop.default_exception_handler(context)

    async def login(self):
        a = await self.sm.get_screen("ImportPage").login(self.session, False)
        logging.info("Login attempt {}.".format("successfull" if a else "failed"))

    def build(self): # build all screens
        run(self.login())
        Window.bind(on_request_close=self.on_request_close)
        self.sm = ScreenManager()
        screens = [
            LoginPage       (self, name="LoginPage"       ),
            SeedgenPage     (self, name="SeedgenPage"     ),
            ImportPage      (self, name="ImportPage"      ),
            UsersPage       (self, name="UsersPage"       ),
            UserPropertyPage(self, name="UserPropertyPage")
        ]

        for i in screens:
            self.sm.add_widget(i)

        self.sm.current = "LoginPage"

        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.handle_exception)

        return self.sm
