import math
import random

from kivy.app import App, Builder
from kivy.core.window import Window

from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget

Window.size = (400, 700)


class BaseWidget(Widget):
    pass

class BaseWidget1(BaseWidget):
    pass

class LoginPage(BaseWidget):
    pass


class UsersPage(BaseWidget1):
    def __init__(self, user=None, **kwargs):
        self.user = user if user else User()
        super().__init__(**kwargs)

    def add_user(self, user):
        self.children[0].children[0].children[0].add_widget(user)

class User(BaseWidget):
    def __init__(self, username="[Username err]", userid="[id err]", index=0, img="app/images/useraccountbase.png", **kwargs):
        self.userid = userid
        self.username = username
        self.index = index
        self.img = img
        
        super().__init__(**kwargs)

    def sqrt(self, width):
        return math.sqrt(width)

class Message(BaseWidget):
    def __init__(self, data="[msgerr]", time="[timeerr]", isleft=False, **kwargs):
        self.data = data
        self.isleft = isleft
        self.lines = len(self.data.split("\n"))
        self.time = time
        super().__init__(**kwargs)

    def sqrt(self, width):
        return math.sqrt(width)

class ScrollLayout(StackLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

class MessagePage(BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_message(Message("\n", ""))

    def add_message(self, message):
        self.children[1].children[0].add_widget(message)

    def update(self, a, b, c):
        a.size[1] = c.size[1]
        b.pos = [0, c.size[1]+10]
        


class Main(App):
    def build(self):
        pass
        # login page
        # return LoginPage()

        # userpage
        # pg =  UsersPage()
        # pg.add_user(User("Username0", "ab247ef933433d32a763d", 0))
        # pg.add_user(User("Username1", "ab247ef933433d32a763d", 1))
        # pg.add_user(User("Username2", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username3", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username4", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username5", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username6", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username7", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username0", "ab247ef933433d32a763d", 0))
        # pg.add_user(User("Username1", "ab247ef933433d32a763d", 1))
        # pg.add_user(User("Username2", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username3", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username4", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username5", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username6", "ab247ef933433d32a763d", 2))
        # pg.add_user(User("Username7", "ab247ef933433d32a763d", 2))
        # return pg

        # message page
        # mp = MessagePage()
        # for i in range(10):
        #     mp.add_message(Message((("hello World!\n"*random.randint(0, 10)) + str(i)), isleft=random.choice([True, False])))

        # return mp


if __name__ == "__main__":
   Main().run()


   