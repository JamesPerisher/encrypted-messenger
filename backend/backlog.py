from sqlalchemy.sql.selectable import Values
from sqlalchemy import update
from backend.packet import *
from backend.db.database import *
from sqlalchemy.future import select
from backend.keymanagement import *

import asyncio
import secrets

class Backlog(object):
    def __init__(self, node) -> None:
        self.node = node
        self.db = node.db
        self.id = self.node.id


class Connector(Backlog):
    def __init__(self, node) -> None:
        super().__init__(node)
        self.conn = None # will eventualy be (reader, writer)
        self.packetlock = asyncio.Lock()

    async def send(self, packet) -> Packet:
        try:
            if not self.conn : self.conn = await asyncio.open_connection(*self.node.get_authority()) # make connection if not exist

            async with self.packetlock: # wait for previouse packet to complete before sending a new one
                self.conn[1].write(packet.read())
                await self.conn[1].drain()

                return await readpacket(*self.conn) # lock prevents this erroring with multiple symultaniouse reads
        except OSError: # network error
            return Packet(PAC.ERR, "net") # TODO: Error handling for this -> frontend render this issue


class Handler(Backlog):
    def __init__(self, node, reader, writer, database) -> None:
        super().__init__(node)
        self.reader = reader
        self.writer = writer
        self.db = database
        self.verify = ""

    async def send(self, packet):
        self.writer.write(packet.read())

    async def serve(self): 
        while True:
            await self.handle(await readpacket(self.reader, self.writer))

    async def handle(self, packet): # handles a valid packet
        return await {
            PAC.RAP: self.rap,
            PAC.NAN: self.nan,
            PAC.INF: self.inf,
            PAC.AUT: self.aut,
            PAC.MSG: self.msg,
            PAC.CRT: self.crt
        }[packet.pactype](packet)

    async def nan(self, packet): pass # do jack shit testing

    async def rap(self, packet): # generate and store data for verifying next message
        data = secrets.token_urlsafe(128)
        self.verify = data
        await self.send(Packet(PAC.RAPA, data))

    async def inf(self, packet):
        users = await self.db.execute(select(User).where(User.userid == packet.data))
        await self.send(Packet(PAC.INFA, [[x["User"].userid, x["User"].name, x["User"].pubkey] for x in users.all()]))

    async def aut(self, packet): pass
    async def msg(self, packet): pass
    async def crt(self, packet):
        if verify(packet.data["pub"], self.verify, packet.data["verify"]):
            if len((await self.db.execute(select(User).where(User.userid == packet.data["id"]))).all()) == 0:
                u = User(userid = packet.data["id"], name = packet.data["uname"], pubkey = packet.data["pub"])
                await self.db.add(u)
            await self.db.execute(update(User).where(User.userid == packet.data["id"]).values(name=packet.data["uname"]))
            return await self.send(Packet(PAC.CRTA, "True"))
        return await self.send(Packet(PAC.CRTA, "False"))
        
        
        
    
