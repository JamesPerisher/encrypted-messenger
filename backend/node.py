import asyncio
import random
import logging
from re import A

from backend.packet import *
from backend.backlog import *

from backend.db.database import *
from backend.keymanagement import *


AUTHORITIES = [("localhost", 6969)]


class Node(object):
    def __init__(self, authorities=AUTHORITIES) -> None:
        self.authorities = authorities
        self.backlog = Connector(self)

    async def check(self, gui, pac):
        if pac.pactype == PAC.ERR:
            return await gui.showerr(pac)
        return pac

    async def send(self, packet):
        return await self.backlog.send(packet)

    def get_authority(self):
        return random.choice(self.authorities)

    async def get_info(self, node): # get info about a node with name or id "node"
        return await self.send(Packet(PAC.INF, node))
    
    async def msg(self, privkey, fromuserid, touserid, data): # send message to node

        pubkey = (await self.get_info(touserid)).data[0][2]
        
        return await self.send(Packet(PAC.MSG, {"from": fromuserid, "to":touserid, "data":encrypt(privkey, pubkey, data.encode())}))


class Authority(Node):
    def __init__(self, capacity, db, authorities=AUTHORITIES) -> None:
        self.capacity = capacity
        self.db = db
        super().__init__(authorities)

    def callback(self, db):
        async def handleclient(reader, writer):
            await Handler(self, reader, writer, db).serve() # create handler for this connection
        return handleclient

    async def start(self):
        server = await asyncio.start_server(self.callback(self.db), "localhost", 6969)
        logging.debug("Serving on {}".format(server.sockets[0].getsockname()))

        async with server:
            await server.serve_forever()


class Client(Node):
    def __init__(self, authorities=AUTHORITIES) -> None:
        super().__init__(authorities)

    async def logout(self):
        self.session.clear()
        await self.session.save()

    async def register(self, id, pubkey):
        data = await self.send(Packet(PAC.RAP, ""))
        data = sign(self.session["privkey"], data.data)

        return await self.send(Packet(PAC.CRT, {"id":id, "pub":pubkey, "verify":data}))
