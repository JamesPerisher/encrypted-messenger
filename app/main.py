import math

from app.usersession import Session
from backend.keymanagement import generate_seed

from kivy.core.window import Window

from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.app import App


Window.size = (400, 700)
SESSION = Session.from_file("userdata/session.json").save() # realy need to store this in secure place idk yet



class ScrollLayout(StackLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

class BaseWidget(Widget):
    pass

class BaseWidget1(BaseWidget):
    pass


class Message(BaseWidget):
    def __init__(self, data="[msgerr]", time="[timeerr]", isleft=False, **kwargs):
        self.data = data
        self.isleft = isleft
        self.lines = len(self.data.split("\n"))
        self.time = time
        super().__init__(**kwargs)

    def sqrt(self, width):
        return math.sqrt(width)


class User(BaseWidget):
    def __init__(self, username="[Username err]", userid="[id err]", index=0, img="app/images/useraccountbase.png", **kwargs):
        self.userid = userid
        self.username = username
        self.index = index
        self.img = img
        
        super().__init__(**kwargs)

    def sqrt(self, width):
        return math.sqrt(width)


class BaseScreen(Screen):
    def __init__(self, sm, **kw):
        self.sm = sm
        super().__init__(**kw)
class BaseScreen1(BaseScreen): pass


class LoginPage(BaseScreen):
    def error(self, txt):
        pass
    def signup(self):
        if self.children[0].children[3].text.strip() == "":
            self.children[0].children[4].text = "Enter a Username"
        elif not (self.children[0].children[2].children[1].active and self.children[0].children[2].children[3].active):
            self.children[0].children[4].text = "You must agree to all terms and conditions"

        else:
            SESSION["username"] = self.children[0].children[3].text.strip()
            self.sm.current = "SeedgenPage"

    def login(self):
        print("importing")


class UsersPage(BaseScreen1):
    def __init__(self, sm, user=None, **kwargs):
        self.user = user if user else User()
        super().__init__(sm, **kwargs)

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
        SESSION["_seed"] = generate_seed()
        other.text = "   ".join(SESSION["_seed"])

    def back(self):
        self.sm.current = "LoginPage"

    def next(self):
        print("next")


class Main(App):
    def build(self):
        self.sm = ScreenManager()
        screens = [
            LoginPage  (self.sm, name="LoginPage"  ),
            SeedgenPage(self.sm, name="SeedgenPage"),
            UsersPage  (self.sm, name="UsersPage"  ),
            MessagePage(self.sm, name="MessagePage")
        ]

        for i in screens:
            self.sm.add_widget(i)

        self.sm.current = "LoginPage"
        # self.sm.current = "SeedgenPage"

        return self.sm


if __name__ == "__main__":
   Main().run()


   