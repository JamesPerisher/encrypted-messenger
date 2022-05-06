from backend.p2p_server import Server
from backend.p2p_utils import Address, Id
from backend.p2p_client import LiveConnection
import sys
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


if __name__ == '__main__':
    args = sys.argv + [""] * 20
    print(args)
    if args[1] == "":
        LiveConnection(Address("iniver.net", 7788), Id.from_time()).run()
    if args[1] == 'server':
        Server(Address("0.0.0.0", 7788)).start()


