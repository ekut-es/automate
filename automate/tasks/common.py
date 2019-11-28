from invoke import task

from ..utils import connection_to_string
import tabulate


@task
def list(c, boards=False, compilers=False):
    "List available boards and compilers"

    if not (boards and compilers):
        boards = True
        compilers = True

    metadata = c['metadata']

    board_table = []
    board_header = ["ID", "Machine", "Cores", "OS", "Connections"]
    if boards:
        for board in metadata.boards:
            os = getattr(board.os, "distribution", "unknown")

            connections = []
            for connection in board.connections:
                s = connection_to_string(connection)
                connections.append(s)

            board_line = [board.id,
                          board.board,
                          len(board.cores),
                          os,
                          ",".join(connections)]

            board_table.append(board_line)

        print("Boards:")
        print(tabulate.tabulate(board_table,
                                headers=board_header))

    return 0
