from backend.p2p_server import Server
from backend.p2p_utils import Address, Id
from backend.p2p_client import LiveConnection
from backend import p2p_server, p2p_client
import sys
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


if __name__ == '__main__':
    args = sys.argv + [""] * 20
    print(args)
    if args[1] == "":
        p2p_client.main()
    if args[1] == 'server':
        p2p_server.main()


