import base64
import time
from hashlib import sha256
from base64 import b64encode

def recv(sock, bytes): # will hang if no data is available
    # Helper function to recv n bytes
    data = b''
    while len(data) < bytes:
        data += sock.recv(bytes - len(data))

    return data

class DeadConnection(Exception):
    pass

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
    def __init__(self, id) -> None:
        self.id = id
    def __repr__(self) -> str:
        return f"Id({self.id})"
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

    @staticmethod
    def idhash(data):
        return b64encode(sha256(str(data).encode()).digest()).decode()

    @classmethod
    def from_time(cls):
        return cls(cls.idhash(time.time()))

    @classmethod
    def from_string(cls, string: str):
        return cls(cls.idhash(string))