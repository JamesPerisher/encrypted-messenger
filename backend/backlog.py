from backend.packet import *
from backend.db.database import *
from sqlalchemy.future import select

import asyncio


class Backlog(object):
    def __init__(self, node) -> None:
        self.node = node
        self.db = node.db
        self.id = self.node.id


class Connector(Backlog):
    def __init__(self, node) -> None:
        super().__init__(node)
        self.conn = None # will eventualy be (reader, writer)

    async def send(self, packet):
        try:
            if not self.conn : self.conn = await asyncio.open_connection(*self.node.get_authority()) # make connif not exist (TODO: Error handling)

            self.conn[1].write(packet.read())
            await self.conn[1].drain()

            return await readpacket(*self.conn)
        except OSError:
            return Packet(PAC.ERR, "net")



class Handler(Backlog):
    def __init__(self, node, reader, writer, database) -> None:
        super().__init__(node)
        self.reader = reader
        self.writer = writer
        self.db = database

    async def send(self, packet):
        self.writer.write(packet.read())

    async def serve(self): 
        while True:
            await self.handle(await readpacket(self.reader, self.writer))

    async def handle(self, packet): # handles a valid packet
        return await {
            PAC.NAN: self.nan,
            PAC.INF: self.inf,
            PAC.AUT: self.aut,
            PAC.MSG: self.msg,
            PAC.CRT: self.crt
        }[packet.pactype](packet)

    async def nan(self, packet): pass # do jack shit testing

    async def inf(self, packet):
        users = await self.db.execute(select(User).where(User.userid == packet.data))
        await self.send(Packet(PAC.INFA, [[x["User"].userid, x["User"].name, x["User"].pubkey] for x in users.all()]))

    async def aut(self, packet): pass
    async def msg(self, packet): pass
    async def crt(self, packet): pass
    
