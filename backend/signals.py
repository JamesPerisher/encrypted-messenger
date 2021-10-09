
from enum import Enum, auto


class PAC(Enum): # need to clear cache everytime this is updated or massive bugs
    PRIV_KEY = auto()
    PUB_KEY  = auto()
    USER_DATA= auto()

class Packet:
    def __init__(self, intent, key) -> None:
        self.intent = intent
        self.key = key

    def read(self):
        return "{}::{}".format(self.intent.value, self.key)

class Event(Enum):
    UNLOCK_PIN   = auto()
    LOGIN        = auto()

    ERROR        = auto()
    ADD_FRIEND   = auto()
    LOGGED_IN    = auto()

    AUTH_ERROR   = auto()
    NET_ERROR    = auto()
    DISCONNECTED = auto()

    NO_USER    = AUTH_ERROR




if __name__ == "__main__":
    print(Packet(PAC.PUB_KEY, "test@localhost").read())
