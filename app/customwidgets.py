from backend.asyncrun import run, asynclambda
from backend.keymanagement import *

from app.shaire import make_code
from app.makepfpic import make_pf_pic

from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder

from kivy.animation import Animation
from kivy.utils import get_color_from_hex

from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.button import Button

import logging


BASE_IMAGE = "app/images/useraccountbase.png"

class MessagePage: # should get overwritten on import
    from_user = lambda : ""


Builder.load_file('app/customwidgets.kv')


class ScrollLayout(StackLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

class BaseWidget(Widget):
    pass

class BaseWidget1(BaseWidget):
    pass

class KVNotifications(BaseWidget):
    def __init__(self, sm, rwidth=0, rheight=0, **kwargs):
        self.rwidth = rwidth
        self.rheight = rheight

        self.anim  = Animation(y=self.rheight+6, duration=0)
        self.anim += Animation(y=self.rheight-self.height, duration=.5, t='in_back')
        self.anim += Animation(y=self.rheight-self.height, duration= 1)
        self.anim += Animation(y=self.rheight+6, duration=.5, t='out_back')

        super().__init__(**kwargs)

class CopyButton(Button):
    data = ""
    async def click(self):
        Clipboard.copy(self.data)
        logging.info("copied \"{}\" to clipboard".format(self.data))

    def on_press(self):
        run(self.click())

class KVPOPup(BaseWidget):
    def __init__(self, sm, rwidth=0, rheight=0, **kwargs):
        self.sm = sm
        self.rwidth = rwidth
        self.rheight = rheight

        self.anim  = Animation(y=self.rheight+6, duration=0)
        self.anim += Animation(y=0.05*self.rheight, duration=.5, t='in_back')
        self.anim += Animation(y=0.05*self.rheight, duration=60*5)

        self.anim1 = Animation(y=self.rheight+6, duration=.5, t='out_back')

        super().__init__(**kwargs)

    async def close(self):
        self.anim1.start(self.children[0])
        self.anim1.bind(on_complete=lambda a,b : self.parent.remove_widget(self))

    def add_widget(self, widget, *args, **kwargs):

        def hmm(widget, *args, **kwargs): # overide add_widget so children[0] is the base widget after children[0] is added
            self.children[0].add_widget(widget, *args, **kwargs)
        self.add_widget = hmm
        return super().add_widget(widget, *args, **kwargs)


class KVPOPupShair(KVPOPup):
    def __init__(self, sm, *args, **kwargs):
        super().__init__(sm, *args, **kwargs)
        make_code("encrypted-msger://user_{}".format(sm.app.session["id"])).save("userdata/shaire.png") # make this async
        
        self.children[0].children[3].source = "userdata/shaire.png"
        self.children[0].children[4].text = sm.app.session["name"]
        self.children[0].children[2].data = sm.app.session["id"]

class KVPOPupChangeName(KVPOPup):
    def __init__(self, sm, *args, **kwargs):
        super().__init__(sm, *args, **kwargs)

    async def change(self):

        session = self.sm.session
                
        session["_privkey"] = change_info(session["_privkey"], self.children[0].children[3].text, None)
        session["pubkey"] = get_pub(session["_privkey"])
        await self.sm.cm.register(session["id"], session["pubkey"])
        session["name"], session["colour"] = get_info(session["pubkey"])

        await self.sm.cm.register(session["id"], session["pubkey"])
        await self.sm.app.reset_UserPage()
        await self.close()

class KVPOPupChangeColour(KVPOPup):
    def __init__(self, sm, *args, **kwargs):
        super().__init__(sm, *args, **kwargs)

    async def change(self):

        session = self.sm.session
                
        session["_privkey"] = change_info(session["_privkey"], None, self.children[0].children[3].colour)
        session["pubkey"] = get_pub(session["_privkey"])
        await self.sm.cm.register(session["id"], session["pubkey"])
        session["name"], session["colour"] = get_info(session["pubkey"])

        await self.sm.cm.register(session["id"], session["pubkey"])
        await self.sm.app.reset_UserPage()
        await self.close()


class KVPOPupSearch(KVPOPup):
    def __init__(self, sm, *args, **kwargs):
        super().__init__(sm, *args, **kwargs)

    async def go(self):

        self.children[0].children[3].text

        await self.close()

class KVPOPupSearch(KVPOPup):
    def __init__(self, sm, *args, **kwargs):
        super().__init__(sm, *args, **kwargs)

    async def go(self):
        data = await self.sm.cm.get_info(self.children[0].children[3].text)

        await self.close()
        if len(data.data) == 0:
            await self.sm.app.shownotification(KVNotifications(self.sm, Window.width, Window.height), "Account not found.")
            return

        await self.sm.app.shownotification(KVPOPupAddUser(self.sm,  User(self.sm, username=data.data[0][1], colour=data.data[0][3], userid=data.data[0][0]), Window.width, Window.height))
        

class KVPOPupAddUser(KVPOPup):
    def __init__(self, sm, user, *args, **kwargs):
        self.user = user
        super().__init__(sm, *args, **kwargs)

    async def go(self): # add user to users in session
        self.sm.session["friends"][self.user.userid] = 1
        await self.sm.session.save()
        await self.sm.app.reset_UserPage()




class BaseScreen(Screen):
    def __init__(self, sm, **kw):
        self.sm = sm
        super().__init__(**kw)
class BaseScreen1(BaseScreen): pass

class ColorInput(Button):
    def __init__(self, colour="#eeeeee", **kwargs):
        self.colour = colour
        super().__init__(**kwargs)

    async def getsm(self):
        a = self
        while True:
            try:
                if isinstance(a.sm, ScreenManager):
                    return a.sm
            except AttributeError:
                pass
            a = a.parent

    async def update(self, colour=None):
        if colour: self.colour = colour
        self.background_color = get_color_from_hex(self.colour)

    async def click(self):
        sm = await self.getsm()

        sm.add_widget(ColourPage(sm, self, sm.current, name="ColourPage"))
        sm.transition.direction = 'left'
        sm.current = "ColourPage"

class ColourPage(BaseScreen):
    def __init__(self, sm, caller, back, **kw):
        super().__init__(sm, **kw)
        self.caller = caller
        self.back = back

    async def done(self):
        self.caller.colour = self.children[0].children[1].hex_color
        await self.caller.update()
        self.sm.remove_widget(self)
        self.sm.transition.direction = 'right'
        self.sm.current = self.back






class UserProperty(BaseWidget): # TODO: idk make all this crap
    def __init__(self, name="namerr", **kw):
        self.name = name
        super().__init__(**kw)
class UserPropertyButton(UserProperty):
    def __init__(self, event=asynclambda(lambda x: x), **kw):
        super().__init__(**kw)
        self.event = event
class UserPropertySpace(UserProperty):
    def __init__(self, **kw):
        super().__init__(name="", **kw)

class User(BaseWidget):
    def __init__(self, sm, username="[Username err]", colour="#eeeeee", userid="[id err]", index=0, img=BASE_IMAGE, **kwargs):
        self.sm = sm
        self.userid = userid
        self.username = username
        self.colour = validate_hex(colour)
        self.index = index
        self.img = img if img != BASE_IMAGE else make_pf_pic(userid, username, colour)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return "<User({}, {})>".format(self.username, self.userid)

    async def press(self):
        name = "MessagePage-{}".format(self.userid)
        if name in self.sm.screen_names:
            self.sm.transition.direction = 'left'
            self.sm.current = name
            return

        self.sm.add_widget(MessagePage.from_user(self.sm, self.parent.parent.parent.parent.user, self, name=name))
        self.sm.transition.direction = 'left'
        self.sm.current = name

    @classmethod
    def from_session(cls, sm, session):
        return cls(sm, session["name"], session["colour"], session["id"])




