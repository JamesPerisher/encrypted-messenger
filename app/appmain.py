import asyncio
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.app import App

from kivy.uix.screenmanager import ScreenManager

import app.customwidgets
from app.customwidgets import *
from backend.basics import BaseObject




Builder.load_file('app/kvsettings.kv')
Builder.load_file('app/appmain.kv')
# Window.size = (400, 700) # for desktop debug only


class LoginPage(BaseScreen):
    async def login(self):
        self.prog.client.displayname   = self.children[0].children[10].text
        self.prog.client.jid           = self.children[0].children[8].text
        self.prog.client.password      = self.children[0].children[6].text
        self.prog.client.displaycolour = self.children[0].children[4].colour


class UsersPage(BaseScreen1):
    def __init__(self, prog, user=None, **kwargs):
        self.user = user if user else User(prog)
        super().__init__(prog, **kwargs)
        run(self.build())
    
    async def build(self): pass
    async def search(self): pass
    async def userproperties(self): pass
    async def shaire(self): pass
    async def add_user(self, user): pass


class MessagePage(BaseScreen):
    def __init__(self, app, meuser, touser, **kwargs):
        super().__init__(app, **kwargs)
        self.meuser = meuser
        self.touser = touser # can be (VirtualUser e.g. a group idk how the encryption would work)
        run(self.make())

    def key(self, other, keyboard, keycode, display, modifyers): pass
    def update(self, a, b, c): pass

    async def ref(self, label, data): pass
    async def make(self): pass
    async def reload(self): pass
    async def send(self): pass
    async def draw_displacement(self, obj): pass
    async def refresh(self): pass
    async def recieve(self, message): pass
    async def back(self): pass

    @classmethod
    def from_user(cls, app, meuser, touser, *args, **kwargs):
        return cls(app, meuser, touser, *args, **kwargs)
app.customwidgets.MessagePage = MessagePage # do import overwrite



class UserPropertyPage(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        run(self.build())

    async def logout(self): pass
    async def changeusername(self): pass
    async def changecolour(self): pass
    async def build(self): pass
    async def add_prop(self, userproperty): pass
    async def back(self): pass

class PinPage(BaseScreen):
    async def next(self, pin):
        print(pin)

from kivy.uix.boxlayout import BoxLayout
class RootLayout(BoxLayout):
    pass

class AppMain(BaseObject, App):
    def __init__(self, prog, **kwargs):
        BaseObject.__init__(self, prog)
        App.__init__(self, **kwargs)
        self.started = asyncio.Event()

    def on_request_close(self, arg): run(self.close())

    async def close(self): pass
    async def reset_UserPage(self): pass

    async def shownotification(self, notificationclass, msg="msgerr", args=()):
        note = notificationclass(self.prog, *args, Window.width, Window.height)
        self.root.add_widget(note, 0)
        if isinstance(note, KVNotifications):
            note.children[0].children[0].text = msg

        note.anim.start(note.children[0])
        note.anim.bind(on_complete=lambda a,b : self.root.remove_widget(note))


    async def update_images(self): pass
    async def login(self): pass


    def build(self): # build all screens
        self.started.set()
        Window.bind(on_request_close=self.on_request_close)
        self.sm = ScreenManager()
        root = RootLayout()

        # create
        self.EmptyPage        = BaseScreen      (self.prog, name="EmptyPage"       ) # overwrite with loadingpage later
        self.LoginPage        = LoginPage       (self.prog, name="LoginPage"       )
        self.PinPage          = PinPage      (self.prog, name="ImportPage"      )
        self.UsersPage        = UsersPage       (self.prog, name="UsersPage"       )
        self.UserPropertyPage = UserPropertyPage(self.prog, name="UserPropertyPage")

        # add
        self.sm.add_widget(self.EmptyPage       )
        self.sm.add_widget(self.LoginPage       )
        self.sm.add_widget(self.PinPage         )
        self.sm.add_widget(self.UsersPage       )
        self.sm.add_widget(self.UserPropertyPage)

        # load
        self.sm.current = self.EmptyPage.name
        root.add_widget(self.sm)
        return root
