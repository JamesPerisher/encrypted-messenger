import logging

from kivy.lang import Builder
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.core.clipboard import Clipboard

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.stacklayout import StackLayout

from backend.config import Config
from backend.signals import Packet, PAC
from backend.makepfp import make_pf_pic
from backend.asyncrun import run, asynclambda
from backend.keymanagement import change_info, contact_data


class MessagePage: # should get overwritten on import
    from_user = lambda : ""

# load myself as a file
Builder.load_file('app/customwidgets.kv')

# height adjusting scroll layout
class ScrollLayout(StackLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

# Base widgets for color only
class BaseWidget(Widget):
    pass
class BaseWidget1(BaseWidget):
    pass

# Base notification clas
class KVNotifications(BaseWidget):
    def __init__(self, prog, rwidth=0, rheight=0, **kwargs):
        self.rwidth = rwidth
        self.rheight = rheight

        self.anim  = Animation(y=self.rheight+6, duration=0)
        self.anim += Animation(y=self.rheight-self.height, duration=.5, t='in_back')
        self.anim += Animation(y=self.rheight-self.height, duration= Config.NOTIFICATION_DISPLAY_TIME)
        self.anim += Animation(y=self.rheight+6, duration=.5, t='out_back')

        super().__init__(**kwargs)

# Copy data to the clicpboard button
class CopyButton(Button):
    data = ""
    async def click(self):
        Clipboard.copy(self.data)
        logging.info("copied \"{}\" to clipboard".format(self.data))

    def on_press(self):
        run(self.click())

# base popup object
class KVPOPup(BaseWidget):
    def __init__(self, prog, rwidth=0, rheight=0, **kwargs):
        self.prog = prog
        self.rwidth = rwidth
        self.rheight = rheight
        self.hidden = False

        self.anim  = Animation(y=self.rheight+6, duration=0)
        self.anim += Animation(y=0.05*self.rheight, duration=.5, t='in_back')
        self.anim += Animation(y=0.05*self.rheight, duration=60*5)

        self.anim1 = Animation(y=self.rheight+6, duration=.5, t='out_back')

        super().__init__(**kwargs)
    
    # touch overide for when hidden
    def on_touch_down(self, touch):
        if self.hidden: return False
        return super().on_touch_down(touch)

    # hide the object
    async def hide(self):
        if self.hidden: return
        self._tmpdata = self.height, self.size_hint_y, self.opacity, self.disabled, self.pos
        self.height, self.size_hint_y, self.opacity, self.disabled, self.pos = 0, None, 0, True, (-1000,-1000)
        self.hidden = True

    # Show the object
    async def show(self):
        if not self.hidden: return
        self.height, self.size_hint_y, self.opacity, self.disabled, self.pos = self._tmpdata
        self.hidden = False

    # close it
    async def close(self):
        self.anim1.start(self.children[0])
        self.anim1.bind(on_complete=lambda a,b : self.parent.remove_widget(self))

    # allows the child of this widget to be treated as the base object
    def add_widget(self, widget, *args, **kwargs):

        def hmm(widget, *args, **kwargs): # overide add_widget so children[0] is the base widget after children[0] is added
            self.children[0].add_widget(widget, *args, **kwargs)
        self.add_widget = hmm
        return super().add_widget(widget, *args, **kwargs)


# Popup to shaire ur account
class KVPOPupShair(KVPOPup):
    def __init__(self, prog, *args, **kwargs):
        super().__init__(prog, *args, **kwargs)
        
        # customized bits
        self.children[0].children[3].source = Config.QRCODE_FILE # shaire image
        self.children[0].children[4].text = self.prog.client.displayname
        self.children[0].children[2].data = self.prog.session.contactstring

# Change Name popup
class KVPOPupChangeName(KVPOPup):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    # eb=vent for changing username
    async def change(self):
        self.prog.session.data["privkey"] = self.prog.session.privkey = change_info(self.prog.session.privkey, self.children[0].children[3].text, None, self.prog.session.pin)
        await self.prog.handler.key_change()
        await self.close()

# same as name change
class KVPOPupChangeColour(KVPOPup):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.children[0].children[3].colour = self.prog.client.displaycolour

    # when color selected hide then move to that page
    async def overide_click(self):
        obj = self.children[0].children[3]
        await self.hide()
        await obj.__class__.click(obj)

    # showmyself and come back when done
    async def overide_update(self):
        obj = self.children[0].children[3]
        await self.show()
        await obj.__class__.update(obj)

    # same as name change
    async def change(self):
        self.prog.session.data["privkey"] = self.prog.session.privkey = change_info(self.prog.session.privkey, None, self.children[0].children[3].colour, self.prog.session.pin)
        await self.prog.handler.key_change()
        await self.close()

# search for other users (Depricated)
class KVPOPupSearch(KVPOPup):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    # do the search (Depricated)
    async def go(self):
        data = contact_data(self.children[0].children[3].text)
        if not data:
            await self.prog.app.shownotification(KVNotifications, "No user for: {}".format(data))
            return
        await self.prog.client.update_roster(data[0])
        await self.prog.app.UsersPage.update()
        await self.close()

# Depricated
class KVPOPupAddUser(KVPOPup):
    def __init__(self, app, user, *args, **kwargs):
        self.user = user
        super().__init__(app, *args, **kwargs)

    async def go(self): # add user to users in session
        pass

# Base screen obejct
class BaseScreen(Screen):
    def __init__(self, prog, **kw):
        self.prog = prog
        super().__init__(**kw)
class BaseScreen1(BaseScreen): pass # copy becouse differentiation makes some thing easyer

# Color input Widget
class ColorInput(Button):
    def __init__(self, colour="#555555", **kwargs):
        self.colour = colour
        super().__init__(**kwargs)

    # gets thescreen manager
    async def getprog(self):
        a = self
        while True:
            try:
                return a.prog
            except AttributeError:
                pass
            a = a.parent

    # when a color is chosen
    async def update(self, colour=None):
        if colour: self.colour = colour
        self.background_color = get_color_from_hex(self.colour)
        self.color = 3*(0 if (sum([x for i,x in enumerate(get_color_from_hex(self.colour)) if i < 4])/3) > 0.5 else 1,)+(1,)

    # when the selector is clicked
    async def click(self):
        prog = await self.getprog()

        prog.app.sm.add_widget(ColourPage(prog, self, prog.app.sm.current, name="ColourPage"))
        prog.app.sm.transition.direction = 'left'
        prog.app.sm.current = "ColourPage"

# Page for colour selecting
class ColourPage(BaseScreen):
    def __init__(self, prog, caller, back, **kw):
        super().__init__(prog, **kw)
        self.caller = caller
        self.back = back

    # we chose a colour yay
    async def done(self):
        self.caller.colour = self.children[0].children[1].hex_color
        await self.caller.update()
        self.prog.app.sm.remove_widget(self)
        self.prog.app.sm.transition.direction = 'right'
        self.prog.app.sm.current = self.back

# Base property
class UserProperty(BaseWidget):
    def __init__(self, name="namerr", **kw):
        self.name = name
        super().__init__(**kw)
# button property
class UserPropertyButton(UserProperty):
    def __init__(self, event=asynclambda(lambda x: x), **kw):
        super().__init__(**kw)
        self.event = event
# spacer
class UserPropertySpace(UserProperty):
    def __init__(self, **kw):
        super().__init__(name="", **kw)

# The Base User class for users in the userpage
class User(BaseWidget):
    def __init__(self, prog, username="Loading...", colour="#eeeeee", userid="Loading..", index=0, img="", **kwargs):
        # all the properties a user has
        self.prog = prog
        self.userid = userid
        self.username = username
        self.colour = "#ff00ff"
        self.index = index
        self.img = make_pf_pic(userid, username, colour)
        super().__init__(**kwargs)

    # make me look pretty
    def __repr__(self) -> str:
        return "<User({}, {})>".format(self.username, self.userid)

    # what to do when the user is clicked
    async def press(self):
        if not await self.prog.session.get_key(self.userid, False): # if we have the pubkey
            return await self.prog.client.send(self.userid, Packet(PAC.GET_PUB)) # get pubkey

        # if we have a messagepage for this user load it
        name = "MessagePage-{}".format(self.userid)
        if name in self.prog.app.sm.screen_names:
            self.prog.app.sm.transition.direction = 'left'
            self.prog.app.sm.current = name
            return

        # create messagepage for this user
        self.prog.app.sm.add_widget(MessagePage.from_user(self.prog, self.parent.parent.parent.parent.user, self, name=name))
        self.prog.app.sm.transition.direction = 'left'
        self.prog.app.sm.current = name

    # Depricated
    @classmethod
    def from_session(cls, app, session):
        return cls(app, session["name"], session["colour"], session["id"])

# Pin Buttons grid layout for pin input
class PinButtons(GridLayout,FocusBehavior):
    # handle keybaord keys
    def keyboard_on_key_down(self, keyboard, keycode, display, modifyers):
        _, code = keycode

        if code in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "backspace", "enter"): # pass on acceptable keys to handler
            # virtualy press the key with the code
            self.children[0].doupdate(code)

# Button for pin input
class PinButton(Button):
    # handle this number being pressed (pass to handler)
    def on_press(self):
        self.color = self._color
        self.doupdate(self.text)
        return super().on_press()

    # deal with keycode
    def doupdate(self, text):
        if len(text) == 1: # assume len == 1 is pin number
            self.parent.data += text
        else:
            if text in ("OK", "enter"): # key press or keybaord codes for continueing
                run(self.parent.callback(self.parent.data))
                self.parent.data = ""
            else:
                self.parent.data = self.parent.data[0:-1]
                
        self.parent.update.text = len(self.parent.data) * "*"

    # reset color
    def on_release(self):
        self.color = self._default
        return super().on_release()
