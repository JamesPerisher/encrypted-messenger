import struct
from aenum import MultiValueEnum
from backend.p2p_utils import recv

class PACKET_TYPE(MultiValueEnum):
    ADDRESS        = 0, "16sI64s"      # ip, port, id
    DOUBLE_ADDRESS = 1, "16sI16sI64s"  # ip, port, ip, port, id


class Packet:
    def __init__(self, type : PACKET_TYPE, *args):
        self.type = type
        self.data = args
    
    def __repr__(self) -> str:
        d = ", ".join(str(x) for x in self.data)
        return f"Packet({self.type.name}, {d})"

    def pack(self):
        # pack string/bytes to bytes
        out = []
        for i in self.data:
            if isinstance(i, str):
                out.append(i.encode('utf-8'))
                continue
            out.append(i)

        data = struct.pack(self.type.values[1], *out)
        return struct.pack(f"II{len(data)}s", len(data), self.type.value, data)

    def send(self, sock):
        return sock.sendall(self.pack())
    

    @classmethod
    def from_bytes(cls, data: bytes):
        # unpack data into packet object
        length, type = struct.unpack(f"II", data[0:8])
        data = data[8:8+length]

        type = PACKET_TYPE(type)
        args = struct.unpack(type.values[1], data)

        # unpack args string/byte to strings
        out = []
        for i in args:
            if isinstance(i, bytes):
                out.append(i.decode('utf-8'))
                continue
            out.append(i)

        return cls(type, *out)

    @classmethod
    def from_socket(cls, sock):
        # unpack data from socket
        lb = recv(sock, 4)
        length = struct.unpack("I", lb)[0]
        type = recv(sock, 4)
        data = recv(sock, length)

        return cls.from_bytes(lb+type+data)


if __name__ == "__main__":
    p = Packet(PACKET_TYPE.ADDRESS, "localhost", 9999, "123456789")
    print(p)
    b = p.pack()
    print(b)
    print(Packet.from_bytes(b))