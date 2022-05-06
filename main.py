from backend.p2p_server import Server
from backend.p2p_utils import Address
import sys
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


if __name__ == '__main__':
    if sys.argv[1] == 'server':
        Server(Address("0.0.0.0", 7788)).start()


