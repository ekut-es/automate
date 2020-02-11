from automate.utils.network import *


def test_find_local_port():
    import socket

    for i in range(10):
        port = find_local_port()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        assert port in range(1024, 65536)

        sock.bind(("0.0.0.0", port))
