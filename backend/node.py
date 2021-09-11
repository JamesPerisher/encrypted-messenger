import asyncio
import random
import logging

from backend.packet import *
from backend.handler import *

from backend.db.database import *
from backend.keymanagement import *
from backend.asyncrun import InputIterator
from backend.cacheproxy import *


AUTHORITIES = [("localhost", 6969)]

class Node:
    def __init__(self, authorities=AUTHORITIES) -> None:
        self.authorities = authorities

class Authority(Node):
    def __init__(self, capacity, db, authorities) -> None:
        super().__init__(authorities=authorities)
        self.capacity = capacity
        self.handlers = list()
        self.db = db

    def callback(self, db):
        async def handleclient(reader, writer):
            handler = Handler(self, reader, writer, db) # create handler for this connection
            self.handlers.append(handler)
            try:
                await handler.serve() # wait for serving to finish then kill this (thread??)
            except:
                logging.info("Killed handler {}".format(handler))
        return handleclient

    async def interactive(self):
        async for i in InputIterator(">>> "):
            if i.strip() == "" : continue
            try:
                print(eval(i))
            except Exception as e:
                print("{}: {}".format(e.__class__.__name__, e))

    async def start(self):
        server = await asyncio.start_server(self.callback(self.db), "localhost", 6969)
        logging.debug("Serving on {}".format(server.sockets[0].getsockname()))

        async with server:
            await server.serve_forever()


class Client(Node):
    def __init__(self, authorities) -> None:
        super().__init__(authorities=authorities)
        self.cache = None # will get set soon
        self.backlog = Connector(self)

    def get_authority(self):
        return random.choice(self.authorities)

    async def send(self, packet):
        return await self.backlog.send(packet)

    async def get_info(self, node): # get info about a node with id "node"
        data = await self.send(Packet(PAC.INF, node))
        # print(data.data[0][2], node) # security mesyure hehe idfk
        return data
    
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

    async def logout(self):
        self.session.clear() # clear login session
        await self.session.save()

        self.cache.clear() # clear cached packages (messages, public keys, etc)
        await self.cache.save()

        for file in os.listdir("userdata"):
            if file in ("README", "session.json", "cache.json") : continue
            os.remove("userdata/{}".format(file))

    async def register(self, id, pubkey):
        await self.session.update()
        data = await self.send(Packet(PAC.RAP, ""))
        data = sign(self.session["_privkey"], data.data)

        return await self.send(Packet(PAC.CRT, {"id":id, "pub":pubkey, "verify":data}))

    async def get_messages_list(self, u1, u2, time):
        return (await self.send(Packet(PAC.MLT, {"u1":u1, "u2":u2, "time": time}))).data

    async def get_msg(self, msgid, datatype):
        return (await self.send(Packet(PAC.GMS, {"id":msgid, "data":datatype}))).data
