import logging
import random
import socket


def find_local_port() -> int:
    """ Returns a locally bindable port number """

    while True:
        port = random.randint(1024, 65536)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("0.0.0.0", port))
            return port
        except:
            logging.debug("Port {} is not bindable".format(port))
