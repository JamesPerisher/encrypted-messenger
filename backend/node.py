import asyncio
import random

from backend.packet import *
from backend.backlog import *

from backend.db.config import *
from backend.db.database import *


AUTHORITIES = [("localhost", 6969)]


class Node(object):
    def __init__(self, id, key, authorities, isauthority) -> None:
        self.id = id
        self.key = key
        self.db = False
        self.authorities = authorities
        self.isauthority = isauthority
        self.backlog = Connector(self)

    async def _start(self, db):
        pass

    async def start(self):
        async with async_session() as session:
            async with session.begin():
                print("Session for db established")
                self.db = True
                await self._start(session)

    async def send(self, packet):
        return await self.backlog.send(packet)

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

    def callback(self, db):
        async def handleclient(reader, writer):
            await Handler(self, reader, writer, db).serve() # create handler for this connection
        return handleclient

    async def _start(self, db):
        server = await asyncio.start_server(self.callback(db), "localhost", 6969)
        print("Serving on {}".format(server.sockets[0].getsockname()))

        async with server:
            await server.serve_forever()



class Client(Node):
    def __init__(self, id, key, authorities) -> None:
        super().__init__(id, key, authorities, isauthority=False)

    async def debug(self):
        print(await self.get_info("test0"))
        print(await self.get_info("testid"))
        print(await self.get_info("test2"))
        print(await self.get_info("test3"))
