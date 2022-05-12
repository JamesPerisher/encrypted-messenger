import logging
from backend.p2p.p2p_utils import Id, Address
from backend.packet import PACKET_TYPE, Packet
import socket

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(asctime)s - %(message)s')


# set loger to log all levels
logger.setLevel(logging.DEBUG)


class Client:
    def __init__(self, conn, address: Address, id: Id) -> None:
        self.conn = conn
        self.address = address
        self.id = id
    def __repr__(self) -> str:
        return f"<Client({self.address}, {self.id})>"

# can only handle one client at at time but client can be defered to another mediator
class Server:
    def __init__(self, bind_address: Address) -> None:
        self.bind_address = bind_address
        self.clients = {}
        self.keep_alive = True

    def stop(self): # stops server
        logger.debug("Server stopping...")
        self.keep_alive = False

    def handle_client(self, conn, addr): # handler one client
        # recieve a client address
        logger.info(f"Connection from: {addr}")

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
            logger.info("Client verified (continuing)")
            self.clients[clientid] = Client(conn, priv_addr, clientid) # register the client
        else:
            logger.info("client not verified (refusing)")
            conn.close()

        logger.info(f"Connection request from: {priv_addr}:{clientid}, to: {data_addr}:{targetid}")

        if targetid in self.clients: # swaps the clients data
            logger.info(f"Client {targetid} found")
            client = self.clients[clientid]
            target = self.clients[targetid]

            logger.info(f"Send client info of {client.id} to client {target.id}")
            Packet(PACKET_TYPE.ADDRESS, *client.address.get(), client.id.get()).send(target.conn)

            logger.info(f"Send client info {target.id} to client {client.id}")
            Packet(PACKET_TYPE.ADDRESS, *target.address.get(), target.id.get()).send(client.conn)

            self.clients.pop(clientid)
            self.clients.pop(targetid)

    def start(self):
        logger.debug(f"Server started... Listening on {self.bind_address}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.bind_address.get())
        s.listen(1)
        s.settimeout(30)

        while self.keep_alive:
            try:
                conn, addr = s.accept()
                addr = Address(*addr)
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break # safe exit
            self.handle_client(conn, addr)
        for i in self.clients.keys(): # close all connections as not to leave clients hanging
            try:
                self.clients[i].conn.close()
            except:
                pass
        logger.debug("Server stopped!")

def main():
    Server(Address("0.0.0.0", 7788)).start()
