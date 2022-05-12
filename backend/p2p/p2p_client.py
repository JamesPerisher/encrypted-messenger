from pickle import TRUE
import socket
import asyncio
from backend.asyncutils import AsyncWrapper, Asyncable, CEvent, isalive, run_async, threadasync
from backend.packet import PACKET_TYPE, Packet
import logging
from threading import Thread
from backend.p2p.p2p_utils import *

logger = logging.getLogger('client')
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(asctime)s - %(message)s')

# set loger to log all levels
logger.setLevel(logging.DEBUG)

class LiveConnection(Asyncable):
    def __init__(self, mediator: Address, myid: Id, target: Id) -> None:
        self.mediator = mediator
        self.myid = myid
        self.target = target
        self.alive = CEvent()
        self.socket = None
        self.keepalive = True

    def __repr__(self) -> str:
        return f"<LiveConnection({self.mediator}, {self.target}, {self.alive})>"

    def kill(self):
        self.keepalive = False

    async def sockready(self, conn, addre: Address):
        print("running baby")
        self.socket = conn
        self.alive.set()
        while self.keepalive: # this is where our connection is established and good to go
            await asyncio.sleep(0.5)
        self.alive.clear()

    def _sockready(self, *args, **kwargs):
        print("start me")
        return run_async(self.sockready(*args, **kwargs))

    def _accept(self, address): # client connection protocal
        logger.info("accept %s", address.port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind(('', address.port)) # accept anything lol might have security issue but fuck it ill deal with it when its a problem
        s.listen(1)
        s.settimeout(5) # wait 5 seconds for connection at a time
        while self.keepalive:
            try:
                conn, addr = s.accept()
                addr = Address(addr[0], addr[1])
                self._sockready(conn, addr)
            except socket.timeout:
                continue

    def _connect(self, local_addr: Address, addr: Address): # client connection protocal
        logger.info(f"connect from {local_addr} to {addr}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind(local_addr.get())

        while self.keepalive:
            try:
                s.connect(addr.get())
                logger.info("connected from %s to %s success!", local_addr, addr)
                self._sockready(s, addr)
            except socket.error:
                continue
            except Exception as exc:
                logger.exception("unexpected exception encountered")
                break

    def _main(self, id: Id): # blocking method
        # make connection to the server
        sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sa.connect(self.mediator.get())

        # get my address
        priv_addr = Address(sa.getsockname()[0], sa.getsockname()[1])

        # send my address to server
        Packet(PACKET_TYPE.ADDRESS, *priv_addr.get(), id.get()).send(sa)

        # recieve back my public address
        ppublic = Packet.from_socket(sa)
        logger.info(f"got public address {ppublic} from private {priv_addr}")

        # send my address again and target
        Packet(PACKET_TYPE.ADDRESS, *priv_addr.get(), self.target.get()).send(sa)

        # where to target
        forignaddress = Packet.from_socket(sa) # recives a double address


        peer_priv_addr = Address(forignaddress[0], forignaddress[1])
        # client_pub_addr  = Address(forignaddress[2], forignaddress[3])
        logger.info(f"found target at {peer_priv_addr}")


        # make threads
        threads = {
            '0_accept': Thread(target=self._accept, args=(priv_addr,)),
            # '1_accept': Thread(target=accept, args=(client_pub_addr[1],)), # not needed?? can use alternative methid if issues come up
            # '2_connect': Thread(target=connect, args=(priv_addr, client_pub_addr,)), 
            '3_connect': Thread(target=self._connect, args=(priv_addr, peer_priv_addr,)),
        }


        # start threads
        for i in sorted(threads.keys()):
            thread = threads[i]
            logger.info(f"starting thread {thread}")
            thread.start()

                #join threads
        while len(threads) > 0 and self.keepalive:
            for i in sorted(threads.keys()):
                thread = threads[i]
                try:
                    thread.join(1)
                except TimeoutError:
                    continue
                if not thread.is_alive():
                    threads.pop(i)

    def run(self):
        try:
            self._main(self.myid)
            return True
        except ConnectionError:
            self.keepalive = False
            self.alive.set()
            return False

# is a async interpreter for a socket connection using Packets
class AsyncConnection(AsyncWrapper):
    def __init__(self, object: Asyncable):
        super().__init__(object)

    def kill(self):
        self.object.kill()

    def start(self, *args, **kwargs):
        return self.object.start(*args, **kwargs)

    @classmethod
    def from_id(cls, myid: Id, targetid: Id, mediator: Address):
        return cls(LiveConnection(mediator, myid, targetid))

    @isalive
    @threadasync
    def recv_packet(self):
        p = Packet.from_socket(self.object.socket)
        return p

    @isalive
    @threadasync
    def send_packet(self, packet: Packet):
        return packet.send(self.object.socket)
        

        
# testing the client
async def comunicate(a, b):
    logger.debug("Testing client")
    try:
        await a.send_packet(Packet(PACKET_TYPE.PING, "Test1"))
        logger.debug("Sent Test1")
        logger.debug(await b.recv_packet())
        await b.send_packet(Packet(PACKET_TYPE.PING, "Test2"))
        logger.debug("Sent Test2")
        logger.debug(await a.recv_packet())
    except DeadConnection as e:
        logger.warning(f"{e}")
    logger.debug("Done testing")

    a.kill()
    b.kill()

# gathering the clients
async def amain():
    a = AsyncConnection(LiveConnection(Address("iniver.net", 7788), Id.from_string("A"), Id.from_string("B")))
    b = AsyncConnection(LiveConnection(Address("iniver.net", 7788), Id.from_string("B"), Id.from_string("A")))

    await asyncio.gather(a.start(), b.start(), comunicate(a, b))


def main():
    asyncio.run(amain())