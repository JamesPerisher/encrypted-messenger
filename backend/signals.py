
from enum import Enum, auto


class PAC(Enum):
    GET_PUB  = auto()
    DEN_PUB  = auto()

    SEND_MSG = auto()
    SEND_PUB = auto()

    INTERNAL = auto()
    ME       = auto()


class Packet:
    def __init__(self, pactype, data="") -> None:
        self.pactype = pactype
        self.data = data
    def __repr__(self) -> str:
        return "{}({}, \"{}\")".format(self.__class__.__name__, self.pactype, self.data)
    @classmethod
    def from_raw(cls, data):
        a, b = data.split("::", 1)
        return cls(PAC(int(a)), b)

    def read(self):
        return "{}::{}".format(self.pactype.value, self.data)


class Event(Enum):
    UNLOCK_PIN    = auto()
    LOGIN         = auto()

    ERROR         = auto()
    ADD_FRIEND    = auto()
    LOGGED_IN     = auto()

    AUTH_ERROR    = auto()
    NET_ERROR     = auto()
    DISCONNECTED  = auto()

    NO_KEY        = auto()

    SEARCH        = auto()
    USER_PROPERTY = auto()
    SHAIRE        = auto()




if __name__ == "__main__":
    print(Packet(PAC.PUB_KEY, "test@localhost").read())
