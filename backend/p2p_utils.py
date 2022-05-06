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

    def get(self):
        return self.ip, self.port


class Id: # user id for heigher level
    def __init__(self, id) -> None:
        self.id = id
    def get(self):
        return self.id

    def idhash(self, data):
        return sha256(str(data).encode()).hexdigest()

    @classmethod
    def from_time(cls):
        return cls(cls.idhash(cls, time.time()))