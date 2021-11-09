import asyncio
import logging

from backend.shaire import make_code

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
from backend.basics import BaseObject

Builder.load_file('app/kvsettings.kv')
Builder.load_file('app/appmain.kv')
# Window.size = (400, 700) # for desktop debug only


class LoginPage(BaseScreen):
    async def signup(self):
        if self.children[0].children[8].text.strip() == "":
            await self.prog.app.shownotification(KVNotifications(self, Window.width, Window.height), "No username.")
        elif not (self.children[0].children[3].children[1].active and self.children[0].children[3].children[3].active):
            await self.app.shownotification(KVNotifications(self, Window.width, Window.height), "You must agree to all terms and conditions.")

        name = self.children[0].children[8].text.strip()
        colour = self.children[0].children[5].colour

    async def login(self):
        self.prog.app.sm.get_screen("ImportPage").backpg = "LoginPage"
        self.prog.app.sm.transition.direction = 'left'
        self.prog.app.sm.current = "ImportPage"


class UsersPage(BaseScreen1):
    def __init__(self, prog, user=None, **kwargs):
        self.user = user if user else User(prog)
        super().__init__(prog, **kwargs)
        run(self.build())
    
    async def build(self):
        make_code("{}://user_{}".format(self.prog.config.APPNAMELINK, "id"), userdata_path=self.prog.config.USERDATA_DIR).save("{}/shaire.png".format(self.prog.config.USERDATA_DIR))

        # async for i in AsyncIterator(self.app.session["friends"]):
        #     data = await self.app.cm.get_info(i)
        #     await self.add_user(User(self.app, data.data[0][1], data.data[0][3], data.data[0][0]))

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

    async def ref(self, label, data): pass

    async def make(self): # load cached messages
        pass

    def key(self, other, keyboard, keycode, display, modifyers):
        _, code = keycode
        if code == "enter" and (not "shift" in modifyers):
            run(self.send())
            return
        other.__class__.keyboard_on_key_down(other, keyboard, keycode, display, modifyers)


    async def reload(self):
        pass
            
    async def send(self):
        pass

    async def draw_displacement(self, obj): # idfk whjat to do with this
        anchors = self.children[0].children[1].children[0].anchors
        lineset = anchors[str(len(anchors)-1)][1] - anchors[str(len(anchors)-2)][1] # distance between a line

        with obj.canvas:
            for key in range(len(anchors)-2):
                Color(*get_color_from_hex(self.colourtable[key]))
                a = obj.height-anchors[str(key)][1] - lineset
                b = obj.height-anchors[str(key+1)][1]
                Line(points=[10, a, 10, b], width=1)
        obj.text = ("\n".join(obj.text.split("\n")[0:-2])) + "\n\n"

    
    async def refresh(self):
        # Clock.schedule_once(lambda x: run(self.draw_displacement(self.children[0].children[1].children[0])), 0) # draw sidebar color thingy
        pass

    async def recieve(self, message): # multiuser message group idk fix this later
        pass

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
        self.prog.app.sm.transition.direction = 'right'
        self.prog.app.sm.current = self.backpg

    def on_pre_enter(self):
        self.children[0].children[2].text = "" # clear seed input box

    async def auth(self, session):
        pass

    async def login (self, session, donote=True):
        pass

    async def signup(self, session):
        pass

    async def next(self): # hadle signing/signup page next button
        pass

from kivy.uix.boxlayout import BoxLayout
class RootLayout(BoxLayout):
    pass

class AppMain(BaseObject, App):
    def __init__(self, prog, **kwargs):
        BaseObject.__init__(self, prog)
        App.__init__(self, **kwargs)

    async def close(self):
        await self.prog.save()
        logging.warn("Exiting program")
        asyncio.get_event_loop().stop()
        return False

    def on_request_close(self, arg): # close asyncio eventloop so program will exit
        run(self.close())

    async def reset_UserPage(self):
        pass

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

    async def login(self):
        pass

    def build(self): # build all screens
        Window.bind(on_request_close=self.on_request_close)
        self.sm = ScreenManager()
        root = RootLayout()
        screens = [
            LoginPage       (self.prog, name="LoginPage"       ),
            ImportPage      (self.prog, name="ImportPage"      ),
            UsersPage       (self.prog, name="UsersPage"       ),
            UserPropertyPage(self.prog, name="UserPropertyPage")
        ]

        for i in screens:
            self.sm.add_widget(i)

        self.sm.current = "LoginPage"


        root.add_widget(self.sm)
        return root
