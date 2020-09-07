from datetime import datetime

import tabulate
from invoke import task

from ..utils import connection_to_string


@task
def show_context(c):  # pragma: no cover
    from pprint import pprint

    pprint(dict(c), indent=2)


@task
def list(c, boards=False, compilers=False):  # pragma: no cover
    """List available boards and compilers

      -b/--boards: only list boards
      -c/--compilers: only list compilers
    """

    if not boards and not compilers:
        boards = True
        compilers = True

    if boards:
        board_table = []
        board_header = [
            "Name",
            "Machine",
            "Cores",
            "OS",
            "Connections",
            "Default Compiler",
            "Lock Status",
        ]
        for board in c.boards():
            os = getattr(board.os, "distribution", "unknown")

            connections = []
            for connection in board.connections:
                s = connection_to_string(connection)
                connections.append(s)

            default_compiler_name = ""
            try:
                default_compiler_name = board.compiler().name
            except:
                pass

            lock_status = "unlocked"
            if board.is_locked() or board.has_lock():
                lock_user = board.lock_holder()
                lock_lease_time_end = datetime.now() + board.lock_lease_time()
                lock_status = (
                    f"locked by {lock_user} until {lock_lease_time_end}"
                )

            board_line = [
                board.name,
                board.board,
                len(board.cores),
                os,
                ",".join(connections),
                default_compiler_name,
                lock_status,
            ]

            board_table.append(board_line)

        print("Boards:")
        print(tabulate.tabulate(board_table, headers=board_header))
        print("")

    if compilers:
        print("Compiler:")

        compiler_table = []
        compiler_header = [
            "Name",
            "Toolchain",
            "Version",
            "Machines",
            "Multiarch",
        ]

        for compiler in c.compilers():
            machines = set()
            for triple in compiler.triples:
                machines.add(triple.machine.value)
            compiler_line = [
                compiler.name,
                compiler.toolchain.value,
                compiler.version,
                ", ".join(sorted(machines)),
                "yes" if compiler.multiarch else "no",
            ]
            compiler_table.append(compiler_line)

        print(tabulate.tabulate(compiler_table, headers=compiler_header))
        print("")

    return 0
