import asyncio
import random

from backend.packet import *
from backend.basehandler import *
from backend.keymanagement import *
from backend.cacheproxy import *

from globalconfig import USERDATA_PATH


class Connector(Backlog):
    def __init__(self, node) -> None:
        super().__init__(node)
        self.conn = None # will eventualy be (reader, writer)
        self.packetlock = asyncio.Lock()

    async def send(self, packet) -> Packet:
        prox = await self.node.cache.get(packet)
        if prox: return prox
        try:
            if not self.conn : self.conn = await asyncio.open_connection(*self.node.get_authority()) # make connection if not exist

            async with self.packetlock: # wait for previouse packet to complete before sending a new one
                self.conn[1].write(packet.read())
                await self.conn[1].drain()

                ret = await readpacket(*self.conn) # lock prevents this erroring with multiple symultaniouse reads
                await self.node.cache.set(packet, ret)
                return ret
        except OSError: # network error
            raise NoNetworkError("No network connection") # TODO: Error handling for this -> frontend render this issue


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

        for file in os.listdir(USERDATA_PATH):
            if file in ("README", "session.json", "cache.json") : continue
            os.remove("{}/{}".format(USERDATA_PATH, file))

    async def register(self, id, pubkey):
        await self.session.update()
        data = await self.send(Packet(PAC.RAP, ""))
        data = sign(self.session["_privkey"], data.data)

        return await self.send(Packet(PAC.CRT, {"id":id, "pub":pubkey, "verify":data}))

    async def get_messages_list(self, u1, u2, time):
        return (await self.send(Packet(PAC.MLT, {"u1":u1, "u2":u2, "time": time}))).data

    async def get_msg(self, msgid, datatype):
        return (await self.send(Packet(PAC.GMS, {"id":msgid, "data":datatype}))).data
