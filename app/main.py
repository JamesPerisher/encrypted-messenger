import kivy
import math
# This will give you ability to use all the different fields as well as methods provided by kivy.
from kivy.app import App

from kivy.uix.widget import Widget
from kivy.core.window import Window



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


class Main(App):
    def build(self):
        # return LoginPage()
        pg =  UsersPage()

        pg.add_user(User("Username0", "ab247ef933433d32a763d", 0))
        pg.add_user(User("Username1", "ab247ef933433d32a763d", 1))
        pg.add_user(User("Username2", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username3", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username4", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username5", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username6", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username7", "ab247ef933433d32a763d", 2))

        pg.add_user(User("Username0", "ab247ef933433d32a763d", 0))
        pg.add_user(User("Username1", "ab247ef933433d32a763d", 1))
        pg.add_user(User("Username2", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username3", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username4", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username5", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username6", "ab247ef933433d32a763d", 2))
        pg.add_user(User("Username7", "ab247ef933433d32a763d", 2))

        return pg


if __name__ == "__main__":
   Main().run()


   