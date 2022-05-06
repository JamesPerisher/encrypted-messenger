import socket
from backend.packet import PACKET_TYPE, Packet
import logging
from threading import Thread
from backend.p2p_utils import *

logger = logging.getLogger('client')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class LiveConnection:
    def __init__(self, mediator: Address, target: Id) -> None:
        self.mediator = mediator
        self.target = target

    def socket(self, conn, addre):
        while True: # this is where our connection is established and good to go
            conn.send(b"test")
            print(conn.recv(4096))
            print(conn.recv(4096))


    def _accept(self, port): # client connection protocal
        logger.info("accept %s", port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind(('', port)) # accept anything lol might have security issue but fuck it
        s.listen(1)
        s.settimeout(5) # wait 5 seconds for connection at a time
        while True:
            try:
                conn, addr = s.accept()
                self.socket(conn, addr)

            except socket.timeout:
                continue
            else:
                logger.info("Accept %s connected!", port)
                # STOP.set()


    def _connect(self, local_addr, addr): # client connection protocal
        logger.info(f"connect from {local_addr} to {addr}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind(local_addr.get())
        while True:
            try:
                s.connect(addr)
                logger.info("connected from %s to %s success!", local_addr, addr)
                self.socket(s, addr)
                break
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
        priv_addr = sa.getsockname()

        # send my address to server
        Packet(PACKET_TYPE.ADDRESS, *priv_addr, id.get()).send(sa)

        # recieve back my public address
        ppublic = Packet.from_socket(sa)
        logger.info(f"got public address {ppublic} from private {priv_addr}")

        # send my address again and target
        Packet(PACKET_TYPE.ADDRESS, *priv_addr, self.target.get()).send(sa)

        # where to target
        forignaddress = Packet.from_socket(sa) # recives a double address


        client_priv_addr = Address(forignaddress[0], forignaddress[1])
        client_pub_addr  = Address(forignaddress[2], forignaddress[3])


        logger.info(f"client_priv_addr {client_priv_addr}, client_pub_addr {client_pub_addr}, id {id}")


        # make threads
        threads = {
            '0_accept': Thread(target=self._accept, args=(priv_addr,)),
            # '1_accept': Thread(target=accept, args=(client_pub_addr[1],)), # not needed??
            # '2_connect': Thread(target=connect, args=(priv_addr, client_pub_addr,)), # not needed?
            '3_connect': Thread(target=self._connect, args=(priv_addr, client_priv_addr,)),
        }


        # start threads
        for i in sorted(threads.keys()):
            thread = threads[i]
            logger.info(f"starting thread {thread}")
            thread.start()

                #join threads
        while len(threads) > 0:
            for i in sorted(threads.keys()):
                thread = threads[i]
                try:
                    thread.join(1)
                except TimeoutError:
                    continue
                if not thread.is_alive():
                    threads.pop(i)

    def run(self):
        self._main(self.target)
        return self




if __name__ == '__main__':
    LiveConnection(Address("iniver.net", 7788), Id.from_time()).run()