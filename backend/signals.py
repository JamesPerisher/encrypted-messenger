
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
    ERROR = auto()
    ADD_FRIEND = auto()
    NO_USER = auto()



if __name__ == "__main__":
    print(Packet(PAC.PUB_KEY, "test@localhost").read())
