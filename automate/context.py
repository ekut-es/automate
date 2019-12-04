import invoke

from .config import AutomateConfig
from .loader import ModelLoader
from .board import BoardHandler


class AutomateContext(invoke.Context):
    def __init__(self, config: AutomateConfig):
        super(AutomateContext, self).__init__(config)

        loader = ModelLoader(config)
        self.metadata = loader.load()

    def boards(self):
        for board in self.metadata.boards:
            yield BoardHandler(board)

    def board(self, board_id: str) -> BoardHandler:
        for board in self.metadata.boards:
            if board.id == board_id:
                return BoardHandler(board)

        raise Exception(
            "Could not find board {} available boards {}".format(
                board_id, ",".join([board.id for board in self.metadata.boards])
            )
        )
