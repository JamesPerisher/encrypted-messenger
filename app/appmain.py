import app.customwidgets
import asyncio

from kivy.lang import Builder
from kivy.core.window import Window

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Line, Color
from kivy.uix.screenmanager import ScreenManager

from app.customwidgets import *
from backend.basics import BaseObject
from backend.asyncrun import AsyncIterator
from backend.keymanagement import encrypt, get_id, get_info, get_pub, validate_hex
from backend.signals import Event


# somehow keeps input visible for keyboard
Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

# preload settings
Builder.load_file('app/kvsettings.kv')
# Window.size = (400, 700) # for desktop debug only

# handle login
class LoginPage(BaseScreen):
    # Stores information
    async def login(self) -> None:
        self.prog.client.displayname   = self.children[0].children[10].text
        self.prog.client.jid           = self.children[0].children[8].text
        self.prog.client.password      = self.children[0].children[6].text
        self.prog.client.displaycolour = self.children[0].children[4].colour

    # move to information page
    async def signup(self) -> None:
        with open(Config.SIGNUP_TEXT, 'r') as f:
            self.prog.app.InfoPage.data = f.read()

        self.prog.app.InfoPage.data += "\n\n\n\n\n\n"
        self.prog.app.InfoPage.halign = "left"

        self.prog.app.InfoPage.backpage = self.name
        self.prog.app.sm.transition.direction = 'left'
        self.prog.app.sm.current = self.prog.app.InfoPage.name

# page to render information to the user
class InfoPage(BaseScreen):
    _data = ""
    _halign = "left"
    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, value):
        self._data = value
        self.children[0].children[0].children[0].text = value # update the kivy widget on valuechange
    
    @property
    def halign(self):
        return self._data
    @data.setter
    def halign(self, value):
        self._halign = value
        self.children[0].children[0].children[0].halign = value # update the kivy widget on valuechange

    backpage = ""

    # go back to the future
    async def back(self):
        self.prog.app.sm.transition.direction = 'right'
        self.prog.app.sm.current = self.backpage

# List of users
class UsersPage(BaseScreen1):
    def __init__(self, prog, user=None, **kwargs):
        self.user = user if user else User(prog)
        self.userlist = {}
        super().__init__(prog, **kwargs)

    # update all users information from new keys
    async def update(self):
        c = self.prog.app.sm.current
        self.user = User(self.prog, self.prog.client.displayname, self.prog.client.displaycolour, get_id(get_pub(self.prog.session.privkey)))

        self.prog.app.sm.remove_widget(self)
        newself=self.__class__(self.prog, self.user, name=self.name)
        self.prog.app.sm.add_widget(newself)
        self.prog.app.sm.current = self.name
        self.prog.app.UsersPage = newself

        async for i in AsyncIterator(await self.prog.client.get_contacts()): # gets contacts from cloud and updates the userlist asyncronously
            u = User(self.prog, *get_info(await self.prog.session.get_key(i)), i)
            await newself.add_user(u)
        self.prog.app.sm.current = c
    
    # Add the user
    async def add_user(self, user):
        self.userlist[user.userid] = user
        self.children[0].children[0].children[0].add_widget(user)

    # Make events on the main program handling
    async def search(self):
        await self.prog.event(Event.SEARCH, "")
    async def userproperties(self):
        await self.prog.event(Event.USER_PROPERTY, "")
    async def shaire(self):
        await self.prog.event(Event.SHAIRE, "")

# Base renderer for messages
class MessagePage(BaseScreen):
    def __init__(self, prog, meuser, touser, **kwargs):
        super().__init__(prog, **kwargs)
        self.meuser = meuser
        self.touser = touser # can be (VirtualUser e.g. a group idk how the encryption would work)
        self.instructions = []
        run(self.reload())

    # do enter events to send messages
    def key(self, other, keyboard, keycode, display, modifyers):
        _, code = keycode
        if code == "enter" and (not "shift" in modifyers):
            run(self.send())
            return
        other.__class__.keyboard_on_key_down(other, keyboard, keycode, display, modifyers)

    # update bottom bar height from text input
    def update(self, a, b, c):
        a.size[1] = c.size[1]
        b.pos = [0, c.size[1]+10]

    async def ref(self, label, data): pass # Depricated

    # load messages from cache
    async def reload(self):
        self.children[0].children[1].children[0].text = self.prog.cache[self.touser.userid]
        run(self.refresh())

    # send message event from kivy
    async def send(self):
        data = self.children[0].children[0].children[1].text
        self.children[0].children[0].children[1].text = ""
        if data.strip() == "": return

        data1 = encrypt(self.prog.session.privkey, await self.prog.session.get_key(self.touser.userid), data.strip(), self.prog.session.pin)
        p = Packet(PAC.SEND_MSG, data1)
        await self.prog.handler.send(self.touser.userid, p, raw=data.strip())
        del data

    # draw pretty bars to left of text
    async def draw_displacement(self, obj): # idfk whjat to do with this
        anchors = self.children[0].children[1].children[0].anchors

        # swap keys and values
        anchors = {v: k for k, v in anchors.items()}
        # sort anchors by key
        anchors = sorted(anchors.items(), key=lambda x: x[0][1])
        anchors.append(((0, obj.height), "#ff0ff")) # add the last anchor for current message block
        # conjoin them in pairs
        anchors = [((anchors[y][0][1], anchors[y+1][0][1]),anchors[y][1]) for y in range(len(anchors)-1)]

        with obj.canvas:
            for i in self.instructions: # clear old instructions
                obj.canvas.remove(i)
            self.instructions = []
            for (y0, y1), key in anchors:
                Color(*get_color_from_hex(validate_hex(key.split("-")[0])))

                a = obj.height-y0-5
                b = obj.height-y1
                self.instructions.append(Line(points=[10, a, 10, b], width=1))

    async def refresh(self):
        Clock.schedule_once(lambda x: run(self.draw_displacement(self.children[0].children[1].children[0])), 0) # draw sidebar color thingy

    async def recieve(self, message): pass # Depricated
    async def back(self): # Go back to the future
        self.prog.app.sm.transition.direction = 'right'
        self.prog.app.sm.current = self.prog.app.UsersPage.name
        await self.prog.cache.save()

    @classmethod
    def from_user(cls, prog, meuser, touser, *args, **kwargs): # create a new instance of the class from user Depricated
        return cls(prog, meuser, touser, *args, **kwargs)
app.customwidgets.MessagePage = MessagePage # do import overwrite


# Change your information
class UserPropertyPage(BaseScreen):
    def __init__(self, prog, **kw):
        super().__init__(prog, **kw)
        run(self.build())

     # Kill everything and close the app
    async def logout(self):
        await self.prog.session.logout()

        self.app.sm.transition.direction = 'right'
        self.app.sm.current = "LoginPage"

    # change username
    async def changeusername(self):
        await self.prog.app.shownotification(KVPOPupChangeName)
    # change colour
    async def changecolour(self):
        await self.prog.app.shownotification(KVPOPupChangeColour)

    # add all the options to the page
    async def build(self):
        await self.add_prop(UserPropertySpace())
        await self.add_prop(UserPropertyButton(name="Change username", event=self.changeusername))
        await self.add_prop(UserPropertyButton(name="Change colour", event=self.changecolour))
        await self.add_prop(UserPropertyButton(name="Log out", event=self.logout))
    async def add_prop(self, userproperty):
        self.children[0].children[0].add_widget(userproperty)
    async def back(self): # Go back to the future
        self.prog.app.sm.transition.direction = 'left'
        self.prog.app.sm.current = self.prog.app.UsersPage.name

# Page for pin number input
class PinPage(BaseScreen):
    pin = ""
    pinevent = asyncio.Event()
    async def next(self, pin): # Depricated
        self.pin = pin
        self.pinevent.set()
    async def setmsg(self, txt): # show prompt
        self.children[0].children[2].text = txt
    
    async def get_pin(self, message): # asyncronousely return after a pin is entered
        await self.focus()
        await self.setmsg(message)
        await self.pinevent.wait() # gets a pin
        p1 = self.pin
        self.pinevent.clear()
        return p1
    
    # refocus keyboard to this object
    async def focus(self):
        self.children[0].children[0].focus = True

    # refocus when losing focus the attention whore
    def on_touch_up(self, touch):
        return
        run(self.focus())

# Overite a default class
from kivy.uix.boxlayout import BoxLayout
class RootLayout(BoxLayout):
    pass

# The pages manager
class AppMain(BaseObject, App):
    def __init__(self, prog, **kwargs):
        BaseObject.__init__(self, prog)
        App.__init__(self, **kwargs)
        self.started = asyncio.Event()

    def on_request_close(self, arg): run(self.prog.close()) # close the app

    # Show a notification
    async def shownotification(self, notificationclass, msg="msgerr", args=()):
        note = notificationclass(self.prog, *args, Window.width, Window.height)
        self.root.add_widget(note, 0)
        if isinstance(note, KVNotifications):
            note.children[0].children[0].text = msg

        note.anim.start(note.children[0])
        note.anim.bind(on_complete=lambda a,b : self.root.remove_widget(note)) # delete notification when animation completes

    # Depricated
    async def update_images(self): pass
    async def login(self): pass


    # Build all the pages
    def build(self):
        self.started.set()
        Window.bind(on_request_close=self.on_request_close)
        self.sm = ScreenManager()
        root = RootLayout()

        # create
        self.EmptyPage        = BaseScreen      (self.prog, name="EmptyPage"       ) # overwrite with loadingpage later idfk
        self.LoginPage        = LoginPage       (self.prog, name="LoginPage"       )
        self.InfoPage         = InfoPage        (self.prog, name="InfoPage"       )
        self.PinPage          = PinPage         (self.prog, name="PinPage"         )
        self.UsersPage        = UsersPage       (self.prog, name="UsersPage"       )
        self.UserPropertyPage = UserPropertyPage(self.prog, name="UserPropertyPage")

        # add
        self.sm.add_widget(self.EmptyPage       )
        self.sm.add_widget(self.LoginPage       )
        self.sm.add_widget(self.InfoPage        )
        self.sm.add_widget(self.PinPage         )
        self.sm.add_widget(self.UsersPage       )
        self.sm.add_widget(self.UserPropertyPage)

        # load
        self.sm.current = self.EmptyPage.name
        root.add_widget(self.sm)
        return root
