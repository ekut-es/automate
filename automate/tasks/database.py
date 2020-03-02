import logging

from invoke import task

from ..model import BoardModelDB, BoardModelFS


@task
def init(c):
    """Initializes the database with default tables"""

    try:
        c.database.init()
    except Exception as e:
        logging.error("Database initialization failed: %s", str(e))


@task
def import_board(c, board, keep=False):
    """Upload a board from local collection to database

       # Arguments
       board: name of the board to upload
       keep: keep yml file in metadata dir
    """

    board = c.board(board, expand=False)

    if isinstance(BoardModelDB):
        logging.error("Board board.id has already been imported to database")

    try:
        c.database.insert_board(board)
    except Exception as e:
        logging.error("%s", str(e))
    else:
        if not keep:
            c.run("rm ")


@task
def export_board(c, board, keep=False):
    """Download board data and save as description.yml in metadata dir

       # Arguments
       board: name of the board
       keep: keep database entry of board
    """

    boards = c.database.get_all_boards()
    board_model = None
    for bm in boards:
        if bm.name == board:
            board_model = bm
            break

    if not board_model:
        logging.error("Could not find board %s in database", board_model)
        return -1
