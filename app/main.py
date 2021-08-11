import asyncio
from backend.asyncrun import run

from backend.keymanagement import generate_seed, generate_key, id_from_priv, id_from_pub, get_pub

from kivy.core.window import Window

from kivy.uix.stacklayout import StackLayout
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.app import App


Window.size = (400, 700) # for desktop debug only


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
    def __init__(self, rwidth=0, rheight=0, **kwargs):
        self.rwidth = rwidth
        self.rheight = rheight

        self.anim  = Animation(y=self.rheight+6, duration=0)
        self.anim += Animation(y=self.rheight-self.height, duration=.5, t='in_back')
        self.anim += Animation(y=self.rheight-self.height, duration= 1)
        self.anim += Animation(y=self.rheight+6, duration=.5, t='out_back')

        super().__init__(**kwargs)


class KVPOPup(BaseWidget):
    def __init__(self, rwidth=0, rheight=0, **kwargs):
        self.rwidth = rwidth
        self.rheight = rheight

        self.anim  = Animation(y=self.rheight+6, duration=0)
        self.anim += Animation(y=0.025*self.rheight, duration=.5, t='in_back')
        self.anim += Animation(y=0.025*self.rheight, duration=60*5)

        self.anim1  = Animation(y=5, duration= .5)
        self.anim1 += Animation(y=self.rheight+6, duration=.5, t='out_back')

        super().__init__(**kwargs)


class Message(BaseWidget):
    def __init__(self, data="[msgerr]", time="[timeerr]", isleft=False, **kwargs):
        self.data = data
        self.isleft = isleft
        self.lines = len(self.data.split("\n"))
        self.time = time
        super().__init__(**kwargs)


class User(BaseWidget):
    def __init__(self, username="[Username err]", userid="[id err]", index=0, img="app/images/useraccountbase.png", **kwargs):
        self.userid = userid
        self.username = username
        self.index = index
        self.img = img
        
        super().__init__(**kwargs)

    @classmethod
    def from_session(cls, session):
        return cls(session["name"], session["id"])


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

    def login(self):
        self.sm.screens[2].backpg = "LoginPage"
        self.sm.session["_seed"] = None
        self.sm.transition.direction = 'left'
        self.sm.current = "ImportPage"


class UsersPage(BaseScreen1):
    def __init__(self, sm, user=None, **kwargs):
        self.user = user if user else User.from_session(sm.session)
        super().__init__(sm, **kwargs)
    
    async def search(self):
        print("looking")

    async def shaire(self):
        self.sm.app.shownotification(KVPOPup(Window.width, Window.height), "Hello World 123!")

    def add_user(self, user):
        self.children[0].children[0].children[0].add_widget(user)


class MessagePage(BaseScreen):
    def __init__(self, sm, **kwargs):
        super().__init__(sm, **kwargs)
        self.add_message(Message("\n", ""))

    def add_message(self, message):
        self.children[1].children[0].add_widget(message)

    def update(self, a, b, c):
        a.size[1] = c.size[1]
        b.pos = [0, c.size[1]+10]


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
            session.save()

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
        session.save()

        self.sm.remove_widget(self.sm.get_screen("UsersPage"))
        self.sm.add_widget(UsersPage(self.sm, User.from_session(session), name="UsersPage"))
        self.sm.current = "UsersPage"

        return True

    async def signup(self, session):
        await self.auth(session)

        a = await self.sm.cm.register(session["id"], session["name"], session["pubkey"])
        print("signup", a)

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

    def shownotification(self, note, msg):
        cc = self.sm.current_screen
        cc.add_widget(note, 0)
        note.children[0].children[0].text = msg
        note.anim.start(note.children[0])

        note.anim.bind(on_complete=lambda a,b : cc.remove_widget(note))


    def build(self): # build all screens
        Window.bind(on_request_close=self.on_request_close)
        self.sm = ScreenManager()
        self.sm.cm = self.cm
        self.sm.session = self.session
        self.sm.app = self
        screens = [
            LoginPage  (self.sm, name="LoginPage"  ),
            SeedgenPage(self.sm, name="SeedgenPage"),
            ImportPage (self.sm, name="ImportPage" ),
            UsersPage  (self.sm, name="UsersPage"  ),
            MessagePage(self.sm, name="MessagePage")
        ]

        for i in screens:
            self.sm.add_widget(i)

        self.sm.current = "LoginPage"
        run(screens[2].login(self.session, False))

        # self.shownotification(KVNotifications(Window.width, Window.height), "Hello World 123!")

        return self.sm


   