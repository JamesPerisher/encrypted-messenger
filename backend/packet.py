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
    NAN  = Val( 0, False) # Non network packet
    RAP  = Val( 1, False) # request auth packet
    ERR  = Val( 2, False) # error with packet
    AERR = Val( 3, False) # Authentication error

    INF = Val(20, False) # request node information
    AUT = Val(30, False) # request authority nodes
    MSG = Val(40, True ) # send message
    CRT = Val(50, True ) # request account creation or updates
    SIG = Val(60, False) # data to be signed
    MLT = Val(70, True ) # request a list of message id's between 2 users
    GMS = Val(80, True ) # request a specific message

    RAPA = Val(11, False) # random data by server
    INFA = Val(21, True ) # responce for INF
    MSGA = Val(41, False) # message aknowlegements
    CRTA = Val(51, False) # acknowlege account creation
    SIGA = Val(61, False) # signed data
    MLTA = Val(71, True ) # list of message id's between 2 users
    GMSA = Val(81, False) # message data


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

    # object defualt functionality
    def __len__(self):
        return self.length
    def __hash__(self) -> int:
        return hash("{}:{}".format(self.pactype, self.data))
    def __eq__(self, o: object) -> bool:
        return self.__hash__() == o.__hash__()
    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)
    def __repr__(self) -> str:
        return "Packet({}, {})".format(self.pactype, "\"{}\"".format(self.data) if isinstance(self.data, str) else self.data)

    @classmethod
    def jimport(cls, data):
        data = json.loads(data)
        return cls(PAC(data["type"]), data["data"])
    def jexport(self):
        return json.dumps({"type":self.pactype.value, "data":self.data})

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
