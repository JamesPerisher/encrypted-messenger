import struct
import enum
import json



class Val(int): # enum value object (int backwards convertability)
    def __init__(self, value, json) -> None:
        self.value = value
        self.json = json
    def __new__(cls, value, json):
        obj = int.__new__(cls, value)
        return obj
    def __hash__(self) -> int:
        return super().__hash__()

# package types
class PAC(enum.Enum):
    NAN = Val( 0, False) # no operation packet
    ERR = Val( 1, False) # error with packet

    INF = Val(20, False) # request node information
    AUT = Val(30, False) # request authority nodes
    MSG = Val(40, True ) # send message
    CRT = Val(50, True ) # request account creation or updates
    SIG = Val(60, False) # data to be signed

    INFA = Val(21, True ) # responce for INF
    CRTA = Val(51, False) # acknowlege account creation
    SIGA = Val(61, False) # signed data


class ReadError(Exception): pass
class Packet(object):
    def __init__(self, pactype, data="") -> None:

        self.data = data
        if pactype.value.json:
            try:
                self.data = json.loads(data)
            except TypeError:
                self.data = data
                self.pactype = PAC.ERR
            self.length = len(json.dumps(self.data))
        else:
            self.length = len(self.data)

        self.valid = True
        self.pactype = pactype

    def __len__(self):
        return self.length

    def __repr__(self) -> str:
        return "Packet({}, {})".format(self.pactype, "\"{}\"".format(self.data) if isinstance(self.data, str) else self.data)

    def read(self):
        if self.valid:
            self.valid = False
             # only compile the data when reading it
            return struct.pack("HH{}s".format(self.length),
            self.length,
            self.pactype.value,(json.dumps(self.data) if self.pactype.value.json else self.data).encode("utf-8")
            )
        raise ReadError("Canot reread packet.")


async def readpacket(reader, writer):
    length, pactype = struct.unpack("HH", await reader.readexactly(4))
    data = await reader.readexactly(length)

    pac = Packet(PAC(pactype), data.decode())
    if pac.pactype == PAC.ERR:
        writer.write(pac)
        await writer.drain()
        writer.close()
    else: return pac
