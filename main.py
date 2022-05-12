from asyncio.log import logger
from backend.p2p import p2p_server, p2p_client
from backend.client import client
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
        elif args.mode == "p2p":
            p2p_client.main()
        elif args.mode == "client":
            client.main()
            
    except SystemExit:
        logger.debug("No mode defaulting to client")
        client.main()
        