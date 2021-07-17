import socket
import asyncio

class Backlog(object):
    def __init__(self, node) -> None:
        self.id = node.id
        self.node = node
        self.data = []

    def add(self, packet):
        self.data.append(packet)

    async def send(self):
        auth = self.node.get_authority()

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setblocking(False)

        loop = asyncio.get_event_loop()
        await loop.sock_connect(soc, self.node.get_authority())
        while len(self.data) != 0:
            current = self.data.pop(0)
            await loop.sock_sendall(soc, current.read())



