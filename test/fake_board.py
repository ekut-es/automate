from pytest import yield_fixture

import mockssh
import os

root_path = os.path.dirname(os.path.abspath(__file__))
test_private_key = os.path.join(root_path, "fake_board_data", "test_id_rsa")
test_public_key = os.path.join(root_path, "fake_board_data", "test_id_rsa.pub")


@yield_fixture()
def board():
    users = {"test": str(test_private_key)}
    with mockssh.Server(users) as s:
        yield s
