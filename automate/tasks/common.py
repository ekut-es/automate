from invoke import task

from ..utils import connection_to_string

import tabulate


@task
def show_context(c):  # pragma: no cover
    from pprint import pprint

    pprint(dict(c), indent=2)


@task
def list(c, boards=False, compilers=False):  # pragma: no cover
    "List available boards and compilers"

    if not boards and not compilers:
        boards = True
        compilers = True

    if boards:
        board_table = []
        board_header = [
            "ID",
            "Machine",
            "Cores",
            "OS",
            "Connections",
            "Default Compiler",
        ]
        for board in c.boards():
            os = getattr(board.os, "distribution", "unknown")

            connections = []
            for connection in board.connections:
                s = connection_to_string(connection)
                connections.append(s)

            default_compiler = board.compiler()

            board_line = [
                board.id,
                board.board,
                len(board.cores),
                os,
                ",".join(connections),
                default_compiler.id,
            ]

            board_table.append(board_line)

        print("Boards:")
        print(tabulate.tabulate(board_table, headers=board_header))
        print("")

    if compilers:
        print("Compiler:")

        compiler_table = []
        compiler_header = [
            "ID",
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
                compiler.id,
                compiler.toolchain.value,
                compiler.version,
                ", ".join(sorted(machines)),
                "yes" if compiler.multiarch else "no",
            ]
            compiler_table.append(compiler_line)

        print(tabulate.tabulate(compiler_table, headers=compiler_header))
        print("")

    return 0
