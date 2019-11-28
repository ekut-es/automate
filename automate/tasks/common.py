from invoke import task

from ..utils import connection_to_string
import tabulate


@task
def show_context(c):
    from pprint import pprint
    pprint(dict(c), indent=2)


@task
def list(c, boards=False, compilers=False):
    "List available boards and compilers"

    if not (boards and compilers):
        boards = True
        compilers = True

    metadata = c['metadata']

    if boards:
        board_table = []
        board_header = ["ID", "Machine", "Cores",
                        "OS", "Connections", "Description"]
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
                          ",".join(connections),
                          board.description]

            board_table.append(board_line)

        print("Boards:")
        print(tabulate.tabulate(board_table,
                                headers=board_header))

    if compilers:
        print("Compiler:")

        compiler_table = []
        compiler_header = ["ID", "Toolchain",
                           "Version", "Machines", "Multiarch"]

        for compiler in metadata.compilers:
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

    return 0
