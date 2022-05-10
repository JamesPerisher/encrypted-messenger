from asyncio.log import logger
from backend.p2p_server import Server
from backend.p2p_utils import Address, Id
from backend.p2p_client import LiveConnection
from backend import p2p_server, p2p_client
import sys
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(asctime)s - %(message)s')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run a p2p server, or client")
    parser.add_argument("mode", choices=["server", "client"], help="Run as a server or a client")

    try:
        args = parser.parse_args()

        if args.mode == "server":
            p2p_server.main()
        elif args.mode == "client":
            p2p_client.main()
    except SystemExit:
        logger.debug("No mode defaulting to client")
        p2p_client.main()
        