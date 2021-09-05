import asyncio
import random
import logging
from re import A

from backend.packet import *
from backend.backlog import *

from backend.db.database import *
from backend.keymanagement import *
from backend.asyncrun import InputIterator


AUTHORITIES = [("localhost", 6969)]


class Node(object):
    def __init__(self, authorities=AUTHORITIES) -> None:
        self.authorities = authorities
        self.backlog = Connector(self)

    async def send(self, packet):
        return await self.backlog.send(packet)

    def get_authority(self):
        return random.choice(self.authorities)

    async def get_info(self, node): # get info about a node with name or id "node"
        return await self.send(Packet(PAC.INF, node))
    
    async def msg(self, privkey, fromuserid, touserid, data): # send message to node

        pubkey = (await self.get_info(touserid)).data[0][2]
        
        encdata = encrypt(privkey, pubkey, data.encode())
        ret = await self.send(Packet(PAC.MSG, 
        {
            "from": fromuserid, "to":touserid,
            "data0":encdata,
            "data1":encrypt(privkey, get_pub(privkey), data.encode())
        }))

        if ret.pactype == PAC.MSGA: return Packet(PAC.MSGA, encdata)


class Authority(Node):
    def __init__(self, capacity, db, authorities=AUTHORITIES) -> None:
        self.capacity = capacity
        self.db = db
        super().__init__(authorities)

    def callback(self, db):
        async def handleclient(reader, writer):
            await Handler(self, reader, writer, db).serve() # create handler for this connection
        return handleclient

    async def interactive(self):
        return
        async for i in InputIterator(": "):
            print(i)

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
        await self.session.update()
        data = await self.send(Packet(PAC.RAP, ""))
        data = sign(self.session["_privkey"], data.data)

        return await self.send(Packet(PAC.CRT, {"id":id, "pub":pubkey, "verify":data}))

    async def get_messages_list(self, u1, u2):
        return (await self.send(Packet(PAC.MLT, {"u1":u1, "u2":u2}))).data

    async def get_msg(self, msgid, datatype):
        return (await self.send(Packet(PAC.GMS, {"id":msgid, "data":datatype}))).data
