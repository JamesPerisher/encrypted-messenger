from backend.asyncrun import AsyncIterator
from backend.keymanagement import *
from backend.db.database import *
from backend.packet import *

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update

import asyncio
import secrets
import logging
import time



class NoNetworkError(Exception): pass

class Backlog(object):
    def __init__(self, node) -> None:
        self.node = node

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
            raise NoNetworkError("No network connection") # TODO: Error handling for this -> frontend render this issue


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
            PAC.CRT: self.crt,
            PAC.MLT: self.mlt,
            PAC.GMS: self.gms
        }[packet.pactype](packet)

    async def nan(self, packet): pass # do jack shit testing

    async def rap(self, packet): # generate and store data for verifying next message
        data = secrets.token_urlsafe(128)
        self.verify = data
        await self.send(Packet(PAC.RAPA, data))

    async def inf(self, packet):
        users = await self.db.execute(select(User).where(User.userid == packet.data))
        out = list()
        async for i in AsyncIterator(users.all()):
            name, colour = get_info(i["User"].pubkey)
            out.append([i["User"].userid, name, i["User"].pubkey, colour])
        return await self.send(Packet(PAC.INFA, out))

    async def aut(self, packet): pass

    async def gms(self, packet):
        ret = (await self.db.execute(select(Message).where(Message.messageid == packet.data["id"]))).all()
        ret = {
            0: ret[0]["Message"].data0,
            1: ret[0]["Message"].data1
            }[packet.data["data"]]

        return await self.send(Packet(PAC.GMSA, ret))
        

    async def mlt(self, packet):
        try:
            u1 = (await self.db.execute(select(User).where(User.userid == packet.data["u1"]))).all()[0]["User"].pubkey
            u2 = (await self.db.execute(select(User).where(User.userid == packet.data["u2"]))).all()[0]["User"].pubkey
        except (IndexError, KeyError, AttributeError, SQLAlchemyError) as e:
            logging.debug('Error at %s', 'division', exc_info=e)
            return await self.send(Packet(PAC.AERR))


        a = await self.db.execute(select(Message).where(
            (Message.fromuserid == packet.data["u1"] and Message.touserid == packet.data["u2"])
            or
            (Message.fromuserid == packet.data["u2"] and Message.touserid == packet.data["u1"])
            ))

        out = []
        async for i in AsyncIterator(a.all()): # inefficent loop
            out.append([i["Message"].creation_time, i["Message"].messageid, i["Message"].fromuserid==packet.data["u1"]])
        return await self.send(Packet(PAC.MLTA, out))
        

    async def msg(self, packet):
        try:
            fromuser = (await self.db.execute(select(User).where(User.userid == packet.data["from"]))).all()[0]["User"].pubkey
            touser   = (await self.db.execute(select(User).where(User.userid == packet.data["to"  ]))).all()[0]["User"].pubkey
        except (IndexError, KeyError, AttributeError, SQLAlchemyError) as e:
            logging.debug('Error at %s', 'division', exc_info=e)
            return await self.send(Packet(PAC.AERR))

        m = Message(
            messageid= get_msg_id(packet.data["from"], packet.data["to"], packet.data["data0"]),
            fromuserid=packet.data["from"],
            touserid=packet.data["to"],
            data0=packet.data["data0"],
            data1=packet.data["data1"],
            creation_time=int(time.time())
            )
        await self.db.add(m)

        return await self.send(Packet(PAC.MSGA))


    async def crt(self, packet):
        if verify(packet.data["pub"], self.verify, packet.data["verify"]): # TODO: use new pgp based verification
            if len((await self.db.execute(select(User).where(User.userid == packet.data["id"]))).all()) == 0:
                u = User(userid = packet.data["id"], pubkey = packet.data["pub"])
                await self.db.add(u)
            await self.db.execute(update(User).where(User.userid == packet.data["id"]).values(pubkey=packet.data["pub"]))
            return await self.send(Packet(PAC.CRTA, "True"))
        return await self.send(Packet(PAC.CRTA, "False"))
        
        
        
    
