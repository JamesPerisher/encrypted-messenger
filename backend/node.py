import asyncio
import random
import socket

from backend.packet import *
from backend.backlog import *


AUTHORITIES = [("localhost", 6969)]


    # def send(self, packet):
    #     self.sock.send(packet.read())

    # def get_id(self, nodeid):
    #     self.send(Packet(PAC_REQ, nodeid))


class Node(object):
    def __init__(self, id, key, authorities, isauthority) -> None:
        self.id = id
        self.key = key
        self.authorities = authorities
        self.isauthority = isauthority
        self.backlog = Backlog(self)

    async def send(self, packet):
        self.backlog.add(packet)

        return await self.backlog.send()


    def get_authority(self):
        return random.choice(self.authorities)

    async def get_info(self, node): # get info about a node with name or id "node"
        return await self.send(Packet(PAC.INF, node))
    
    async def msg(self, nodeid, data): # send message to node
        return await self.send(Packet(PAC.INF, "{}:{}".format(nodeid, data)))



class Authority(Node):
    def __init__(self, id, key, authorities, capacity) -> None:
        self.capacity = capacity
        super().__init__(id, key, authorities, True)

    async def handleclient(self, conn):
        print(await readpacket(conn))


    async def startserver(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 6969))
            s.listen(self.capacity)
            s.setblocking(False)


            loop = asyncio.get_event_loop()

            while True:
                conn, _ = await loop.sock_accept(s)
                loop.create_task(self.handleclient(conn))

                print("connection")




class Client(Node):
    def __init__(self, id, key, authorities) -> None:
        super().__init__(id, key, authorities, isauthority=False)

    async def debug(self):
        print(await self.get_info("test"))
