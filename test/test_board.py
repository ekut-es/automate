import io

from fabric import Connection

from fake_board import board, test_private_key


def test_fake_board(board, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))

    host = board.host
    port = board.port
    user = "test"

    con = Connection(
        user=user,
        host=host,
        port=port,
        connect_kwargs={"key_filename": test_private_key},
    )
    con.open()

    assert con.is_connected == True

    print("ls /")
    con.run("ls /")
