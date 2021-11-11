
from enum import Enum, auto

# Packet types
class PAC(Enum):
    GET_PUB  = auto() # request the public key

    SEND_MSG = auto() # send a message
    SEND_PUB = auto() # send a public key

    # not interpreted from the net
    INTERNAL = auto() # send raw message to myself
    ME       = auto() # send formattable message to myself

# Packet object
class Packet:
    def __init__(self, pactype, data="") -> None:
        self.pactype = pactype
        self.data = data
    # me looks pretty
    def __repr__(self) -> str:
        return "{}({}, \"{}\")".format(self.__class__.__name__, self.pactype, self.data)
    # make from raw data
    @classmethod
    def from_raw(cls, data):
        a, b = data.split("::", 1)
        return cls(PAC(int(a)), b)
    # get raw data
    def read(self):
        return "{}::{}".format(self.pactype.value, self.data)

# event types
class Event(Enum):
    UNLOCK_PIN    = auto() # request unlocking of pin
    LOGIN         = auto() # request login

    ERROR         = auto() # we had an eror
    ADD_FRIEND    = auto() # add a friend
    LOGGED_IN     = auto() # we logged in

    AUTH_ERROR    = auto() # we had authentication error
    NET_ERROR     = auto() # we had a network error
    DISCONNECTED  = auto() # we disconected

    NO_KEY        = auto() # we have no key

    SEARCH        = auto() # we want to search
    USER_PROPERTY = auto() # we want to go to user property page
    SHAIRE        = auto() # we want to shaire