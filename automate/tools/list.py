import tabulate

from ..loader import get_model
from .base import ToolBase
from ..utils import connection_to_string


class ListTool(ToolBase):
    "List all available boards and compilers"

    def run(self) -> int:
        board_table = []
        board_header = ["ID", "Machine", "Cores", "OS", "Connections"]
        for board in self.model.boards:
            os = getattr(board.os, "distribution", "unknown")

            connections = [connection_to_string(
                connection) for connection in board.connections]
            board_line = [board.id,
                          board.board,
                          len(board.cores),
                          os,
                          ",".join(connections)]

            board_table.append(board_line)

        print(tabulate.tabulate(board_table,
                                headers=board_header))

        return 0


if __name__ == "__main__":
    tool = ListTool()
    tool.run()
