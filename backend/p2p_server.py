import logging
from backend.p2p_utils import Id, Address
from backend.packet import PACKET_TYPE, Packet
from backend.tcp_util import *
import socket

logger = logging.getLogger()
clients = {}


class Server:
    def __init__(self, bind_address: Address) -> None:
        self.bind_address = bind_address

    def start(self):
        logger.info("server started")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.bind_address.get())
        s.listen(1)
        s.settimeout(30)

        while True:
            try:
                conn, addr = s.accept()
                addr = Address(*addr)
            except socket.timeout:
                continue

            # recieve a client address
            logger.info(f"connection address: {addr}")

            ip, port, id = Packet.from_socket(conn).data
            priv_addr, id1 = Address(ip, port), Id(id)

            # send back the address
            Packet(PACKET_TYPE.ADDRESS, *priv_addr.get(), id1.get()).send(conn)

            # client address 2
            ip, port, id = Packet.from_socket(conn).data
            data_addr, id2 = Address(ip, port), Id(id)
            




            if data_addr == addr:
                logger.info('client reply matches')
                clients[addr] = Client(conn, addr, priv_addr)
            else:
                logger.info('client reply did not match')
                conn.close()

            logger.info(f"private addre: {priv_addr}, data addr: {data_addr}")

            if len(clients) == 2:
                # send clients data on where to connect
                (addr1, c1), (addr2, c2) = clients.items()
                logger.info('server - send client info to: %s', c1.pub)
                send_msg(c1.conn, c2.peer_msg())
                logger.info('server - send client info to: %s', c2.pub)
                send_msg(c2.conn, c1.peer_msg())
                clients.pop(addr1)
                clients.pop(addr2)

        conn.close()


if __name__ == '__main__':
    Server(Address("0.0.0.0", 7788)).start()
