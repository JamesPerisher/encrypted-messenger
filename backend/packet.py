import struct
import asyncio
import enum



# package types
class PAC(enum.Enum):
    NAN = 0 # no operation packet
    INF = 1 # request node information
    AUT = 2 # request authority nodes

    MSG = 10 # send message


class ReadError(Exception): pass

class Packet(object):
    def __init__(self, pactype, data="") -> None:
        self.valid = True
        self.pactype = pactype
        self.length = len(data)
        self.data = data

    def __len__(self):
        return self.length

    def __repr__(self) -> str:
        return "Packet({}, \"{}\")".format(self.pactype, self.data)

    def read(self):
        if self.valid:
            self.valid = False
            return struct.pack("HH{}s".format(self.length), self.length, self.pactype.value , self.data.encode("utf-8")) # only compile the data when reading it
        raise ReadError("Canot reread packet.")


async def readpacket(sock):
    loop = asyncio.get_event_loop()
    
    length, pactype = struct.unpack("HH", await loop.sock_recv(sock, 4))
    data = await loop.sock_recv(sock, length)

    return Packet(PAC(pactype), data.decode("utf-8"))




if __name__ == "__main__":
    a = Packet(PAC.NAN, "0123456789")
    print(a.length, a.read(), len(a.rawdata))
    # print(a.read())
