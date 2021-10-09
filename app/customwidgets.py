from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder

from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.app import App

from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.button import Button

import logging

from backend.asyncrun import run, asynclambda


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
    def __init__(self, prog, rwidth=0, rheight=0, **kwargs):
        self.rwidth = rwidth
        self.rheight = rheight

        self.anim  = Animation(y=self.rheight+6, duration=0)
        self.anim += Animation(y=self.rheight-self.height, duration=.5, t='in_back')
        self.anim += Animation(y=self.rheight-self.height, duration= prog.config.NOTIFICATION_DISPLAY_TIME)
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
    def __init__(self, app, rwidth=0, rheight=0, **kwargs):
        self.app = app
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
    def __init__(self, prog, *args, **kwargs):
        super().__init__(prog, *args, **kwargs)
        
        # self.children[0].children[3].source = "{}/shaire.png".format(prog.a) # shaire image
        self.children[0].children[4].text = "hmm" # name
        self.children[0].children[2].data = "hmm" # id

class KVPOPupChangeName(KVPOPup):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    async def change(self):
        pass

class KVPOPupChangeColour(KVPOPup):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    async def change(self):
        pass

class KVPOPupSearch(KVPOPup):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    async def go(self):

        await self.close()

class KVPOPupSearch(KVPOPup):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    async def go(self):
        data = await self.app.cm.get_info(self.children[0].children[3].text)

        await self.close()
        if len(data.data) == 0:
            await self.app.shownotification(KVNotifications(self.app, Window.width, Window.height), "Account not found.")
            return

        await self.app.shownotification(KVPOPupAddUser(self.app,  User(self.app, username=data.data[0][1], colour=data.data[0][3], userid=data.data[0][0]), Window.width, Window.height))
        

class KVPOPupAddUser(KVPOPup):
    def __init__(self, app, user, *args, **kwargs):
        self.user = user
        super().__init__(app, *args, **kwargs)

    async def go(self): # add user to users in session
        self.app.session["friends"][self.user.userid] = 1
        await self.app.session.save()
        await self.app.reset_UserPage()




class BaseScreen(Screen):
    def __init__(self, prog, **kw):
        self.prog = prog
        super().__init__(**kw)
class BaseScreen1(BaseScreen): pass

class ColorInput(Button):
    def __init__(self, colour="#eeeeee", **kwargs):
        self.colour = colour
        super().__init__(**kwargs)

    async def getprog(self):
        a = self
        while True:
            try:
                return a.prog
            except AttributeError:
                pass
            a = a.parent

    async def update(self, colour=None):
        if colour: self.colour = colour
        self.background_color = get_color_from_hex(self.colour)

    async def click(self):
        prog = await self.getprog()

        prog.app.sm.add_widget(ColourPage(prog, self, prog.app.sm.current, name="ColourPage"))
        prog.app.sm.transition.direction = 'left'
        prog.app.sm.current = "ColourPage"

class ColourPage(BaseScreen):
    def __init__(self, prog, caller, back, **kw):
        super().__init__(prog, **kw)
        self.caller = caller
        self.back = back

    async def done(self):
        self.caller.colour = self.children[0].children[1].hex_color
        await self.caller.update()
        self.prog.app.sm.remove_widget(self)
        self.prog.app.sm.transition.direction = 'right'
        self.prog.app.sm.current = self.back

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
    def __init__(self, prog, username="[Username err]", colour="#eeeeee", userid="[id err]", index=0, img="", **kwargs):
        self.prog = prog
        self.userid = userid
        self.username = username
        self.colour = "#ff00ff"
        self.index = index
        self.img = ""
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return "<User({}, {})>".format(self.username, self.userid)

    async def press(self):
        name = "MessagePage-{}".format(self.userid)
        if name in self.app.sm.screen_names:
            self.app.sm.transition.direction = 'left'
            self.app.sm.current = name
            return

        self.app.sm.add_widget(MessagePage.from_user(self.app, self.parent.parent.parent.parent.user, self, name=name))
        self.app.sm.transition.direction = 'left'
        self.app.sm.current = name

    @classmethod
    def from_session(cls, app, session):
        return cls(app, session["name"], session["colour"], session["id"])




