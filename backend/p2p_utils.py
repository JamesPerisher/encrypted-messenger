import time
from hashlib import sha256

def recv(sock, bytes): # will hang if no data is available
    # Helper function to recv n bytes
    data = b''
    while len(data) < bytes:
        data += sock.recv(bytes - len(data))

    return data




class Address: # network address for heigher level
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
    def __repr__(self) -> str:
        return f"Address({self.ip}, {self.port})"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Address):
            return self.ip == __o.ip and self.port == __o.port
        return False
    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)
    def __hash__(self) -> int:
        return [self.ip, self.port].__hash__()

    def get(self):
        return self.ip, self.port


class Id: # user id for heigher level
    def __init__(self, id, display="") -> None:
        self.id = id
        self.display = display
    def __repr__(self) -> str:
        return f"Id({self.get()}, {self.display})"
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Id): # becouse cant have self referential types WHYYYYYYYYYYYYY!!
            return self.id == __o.id
        return False
    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)
    def __hash__(self) -> int:
        return self.id.__hash__()

    def get(self):
        return self.id

    def idhash(self, data):
        return sha256(str(data).encode()).hexdigest()

    @classmethod
    def from_time(cls):
        return cls(cls.idhash(cls, time.time()))

    @classmethod
    def from_string(cls, string: str):
        return cls(cls.idhash(cls, string), string)