from . import common
from . import compiler
from . import board

from invoke import Collection

compiler_tasks = Collection().from_module(compiler)
board_tasks = Collection().from_module(board)

collection = Collection().from_module(common)
collection.add_collection(compiler_tasks)
collection.add_collection(board_tasks)
