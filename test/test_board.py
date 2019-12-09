from fake_board import board, test_private_key

from fabric import Connection


def test_fake_board(board):
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
