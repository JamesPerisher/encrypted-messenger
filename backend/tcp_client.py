import sys
import logging
import socket
import struct
from threading import Event, Thread
from backend.tcp_util import *


logger = logging.getLogger('client')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
STOP = Event()


def accept(port):
    logger.info("accept %s", port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('', port))
    s.listen(1)
    s.settimeout(5)
    while not STOP.is_set():
        try:
            conn, addr = s.accept()

            while True:
                conn.send(b"test")
                print(conn.recv(4096))
        except socket.timeout:
            continue
        else:
            logger.info("Accept %s connected!", port)
            # STOP.set()


def connect(local_addr, addr):
    logger.info("connect from %s to %s", local_addr, addr)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(local_addr)
    print("connecting baby")
    while not STOP.is_set():
        try:
            s.connect(addr)

            while True:
                s.send(b"hello")
                print(s.recv(4096))
        except socket.error:
            continue
        # except Exception as exc:
        #     logger.exception("unexpected exception encountered")
        #     break
        else:
            logger.info("connected from %s to %s success!", local_addr, addr)
            # STOP.set()


def main(host='server', port=5005):
    # make connection to the server
    sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sa.connect((host, port))
    priv_addr = sa.getsockname() # get my address

    send_msg(sa, addr_to_msg(priv_addr)) # send my address to server
    data = recv_msg(sa) # recieve back my address
    logger.info("client %s %s - received data: %s", priv_addr[0], priv_addr[1], data)
    pub_addr = msg_to_addr(data)
    send_msg(sa, addr_to_msg(pub_addr)) # send y address again

    data = recv_msg(sa) # where to target
    pubdata, privdata = data.split(b'|')
    client_pub_addr = msg_to_addr(pubdata)
    client_priv_addr = msg_to_addr(privdata)
    logger.info(
        "client public is %s and private is %s, peer public is %s private is %s",
        pub_addr, priv_addr, client_pub_addr, client_priv_addr,
    )

    threads = {
        '0_accept': Thread(target=accept, args=(priv_addr[1],)),
        # '1_accept': Thread(target=accept, args=(client_pub_addr[1],)), # not needed??
        # '2_connect': Thread(target=connect, args=(priv_addr, client_pub_addr,)), # not needed?
        '3_connect': Thread(target=connect, args=(priv_addr, client_priv_addr,)),
    }
    for name in sorted(threads.keys()):
        logger.info('start thread %s', name)
        threads[name].start()

    while threads:
        keys = list(threads.keys())
        for name in keys:
            try:
                threads[name].join(1)
            except TimeoutError:
                continue
            if not threads[name].is_alive():
                threads.pop(name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, message='%(asctime)s %(message)s')
    main('iniver.net', 7788)
