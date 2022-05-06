import logging
from backend.p2p_utils import Id, Address
from backend.packet import PACKET_TYPE, Packet
from backend.tcp_util import *
import socket

logger = logging.getLogger()


class Client:
    def __init__(self, conn, address: Address, id: Id) -> None:
        self.conn = conn
        self.address = address
        self.id = id

class Server:
    def __init__(self, bind_address: Address) -> None:
        self.bind_address = bind_address
        self.clients = {}

    def handle_client(self, conn, addr):
        # recieve a client address
        logger.info(f"connection address: {addr}")

        ip, port, clientid = Packet.from_socket(conn).data
        priv_addr, clientid = Address(ip, port), Id(clientid)

        # send back the address
        Packet(PACKET_TYPE.ADDRESS, *priv_addr.get(), clientid.get()).send(conn)

        # client address 2
        ip, port, id = Packet.from_socket(conn).data
        data_addr, targetid = Address(ip, port), Id(id)

        # check if client address matches will fail if tampered with half way through
        logger.debug(f"Addresses: {priv_addr}, {data_addr}")
        if priv_addr == data_addr: # could do key verification here as well
            logger.info("client partialy verified")
            self.clients[clientid] = Client(conn, priv_addr, clientid) # register the client
        else:
            logger.info("client not verified")
            conn.close()

        logger.info(f"private addre: {priv_addr}, data addr: {data_addr}")

        if targetid in self.clients:
            logger.info(f"client {targetid} found")
            client = self.clients[clientid]
            target = self.clients[targetid]

            logger.info(f"send client info of {client.id} to client {target.id}")
            Packet(PACKET_TYPE.ADDRESS, *client.address.get(), client.id.get()).send(target.conn)

            logger.info(f"send client info {target.id} to client {client.id}")
            Packet(PACKET_TYPE.ADDRESS, *target.address.get(), target.id.get()).send(client.conn)

            self.clients.pop(clientid)
            self.clients.pop(targetid)

        logger.info(f"client list: {self.clients}")


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
            except KeyboardInterrupt:
                break # safe exit
            self.handle_client(conn, addr)
        for i in self.clients.keys(): # close all connections
            if self.clients[i].conn.is_alive():
                self.clients[i].conn.close()
        logger.info("server stopped")


if __name__ == '__main__':
    Server(Address("0.0.0.0", 7788)).start()
