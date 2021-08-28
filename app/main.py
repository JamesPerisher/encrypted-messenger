import asyncio

from backend.asyncrun import run, asynclambda
from backend.backlog import NoNetworkError
from backend.shaire import make_code
from backend.keymanagement import generate_seed, generate_key, id_from_priv, id_from_pub, get_pub

from kivy.core.window import Window

from kivy.uix.stacklayout import StackLayout
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.app import App


Window.size = (400, 700) # for desktop debug only

# gi.require_version('Gst', '1.0')
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
        
        self.children[0].children[1].source = "userdata/shaire.png"
        self.children[0].children[2].text = sm.app.session["name"]

class KVPOPupChangeName(KVPOPup):
    def __init__(self, sm, *args, **kwargs):
        super().__init__(sm, *args, **kwargs)

    async def change(self):

        session = self.sm.session
        session["name"] = self.children[0].children[3].text

        await self.sm.cm.register(session["id"], session["name"], session["pubkey"])
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

        await self.sm.app.shownotification(KVPOPupAddUser(self.sm,  User(self.sm, username=data.data[0][1], userid=data.data[0][0]), Window.width, Window.height))
        

class KVPOPupAddUser(KVPOPup):
    def __init__(self, sm, user, *args, **kwargs):
        self.user = user
        super().__init__(sm, *args, **kwargs)

    async def go(self): # add user to users in session
        self.sm.session["friends"][self.user.userid] = 1
        await self.sm.session.save()
        await self.sm.app.reset_UserPage()


class MessageImg(Image):
    def __init__(self, message, **kwargs):
        self.user = message.from_user
        self.colour = message.colour
        self.size = (2*message.line_height, ) *2
        super().__init__(**kwargs)

class Message(TextInput):
    def __init__(self, from_user, text="error", time="[timeerr]", colour="#ff00ffff", foreground_color="#ffffffff", **kwargs):
        self.from_user = from_user
        self.foreground_colora=foreground_color
        self.time = time
        self.colour = colour
        super().__init__(text=text, **kwargs)

    def get_width(self):
        return Window.width


class User(BaseWidget):
    def __init__(self, sm, username="[Username err]", userid="[id err]", index=0, img="app/images/useraccountbase.png", **kwargs):
        self.sm = sm
        self.userid = userid
        self.username = username
        self.index = index
        self.img = img
        
        super().__init__(**kwargs)

    async def press(self):
        self.sm.remove_widget(self.sm.get_screen("MessagePage"))
        self.sm.add_widget(MessagePage.from_user(self.sm, self, name="MessagePage"))
        self.sm.transition.direction = 'left'
        self.sm.current = "MessagePage"

    @classmethod
    def from_session(cls, sm, session):
        return cls(sm, session["name"], session["id"])


class BaseScreen(Screen):
    def __init__(self, sm, **kw):
        self.sm = sm
        super().__init__(**kw)
class BaseScreen1(BaseScreen): pass


class LoginPage(BaseScreen):
    def signup(self):
        if self.children[0].children[3].text.strip() == "":
            self.children[0].children[4].text = "Enter a Username"
        elif not (self.children[0].children[2].children[1].active and self.children[0].children[2].children[3].active):
            self.children[0].children[4].text = "You must agree to all terms and conditions"

        else:
            self.children[0].children[4].text = ""
            self.sm.session["name"] = self.children[0].children[3].text.strip()
            self.sm.transition.direction = 'left'
            self.sm.current = "SeedgenPage"

    def on_pre_enter(self):
        self.children[0].children[4].text = ""

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
        for i in self.sm.session["friends"]:
            data = await self.sm.cm.get_info(i)
            await self.add_user(User(self.sm, data.data[0][1], data.data[0][0]))

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
    def __init__(self, sm, meuser, **kwargs):
        self.meuser = meuser
        super().__init__(sm, **kwargs)

    async def add_message(self, message):
        # self.children[0].children[1].children[0].height += message.children[0].minimum_height+2
        # self.children[0].children[1].children[0].add_widget(MessageImg(message))
        self.children[0].children[1].children[0].add_widget(Message(message.from_user, message.from_user.username, colour="#00000000", foreground_color=message.colour))
        self.children[0].children[1].children[0].add_widget(message)
    
    async def send(self):
        await self.add_message(Message(self.meuser, self.children[0].children[0].children[1].text))
        self.children[0].children[0].children[1].text = ""
    
    async def recieve(self): # multiuser message group idk fix this later
        await self.add_message(Message(self.meuser, self.children[0].children[0].children[1].text))

    async def back(self):
        self.sm.transition.direction = 'right'
        self.sm.current = "UsersPage"

    def update(self, a, b, c):
        a.size[1] = c.size[1]
        b.pos = [0, c.size[1]+10]

    @classmethod
    def from_user(cls, sm, meuser, *args, **kwargs):
        return cls(sm, meuser, *args, **kwargs)

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

        

    async def build(self):
        await self.add_prop(UserPropertySpace())
        await self.add_prop(UserPropertyButton(name="Change username", event=self.changeusername))
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
            session["privkey"] = generate_key(session["_seed"])
            session["id"] = id_from_priv(session["privkey"])
            session["pubkey"] = get_pub(session["privkey"])
            await session.save()

    async def login (self, session, donote=True):
        await self.auth(session)

        userdata = await self.sm.cm.get_info(session["id"])
        if userdata.data == []:
            if donote:
                Clock.schedule_once(lambda x: self.on_pre_enter("No user for provided seed."), 0) # TODO: proper error notification
            return False
        
        session["id"]     = userdata.data[0][0]
        session["name"]   = userdata.data[0][1]
        session["pubkey"] = userdata.data[0][2]
        await session.save()

        await self.sm.app.reset_UserPage()
        self.sm.current = "UsersPage"

        return True

    async def signup(self, session):
        await self.auth(session)
        await self.sm.cm.register(session["id"], session["name"], session["pubkey"])

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
        super().__init__(**kwargs)

    def on_request_close(self, arg): # close asyncio eventloop so program will exit
        print("Exiting program")
        asyncio.get_event_loop().stop()
        return False

    async def reset_UserPage(self):
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
            MessagePage     (self.sm, "", name="MessagePage"     ),
            UserPropertyPage(self.sm, name="UserPropertyPage")
        ]

        for i in screens:
            self.sm.add_widget(i)

        self.sm.current = "LoginPage"
        run(screens[2].login(self.session, False))


        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.handle_exception)

        return self.sm


   