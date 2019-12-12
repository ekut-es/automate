from . import common
from . import compiler
from . import board
from . import admin
from . import cmake
from . import kernel

from invoke import Collection

compiler_tasks = Collection().from_module(compiler)
board_tasks = Collection().from_module(board)
admin_tasks = Collection().from_module(admin)
cmake_tasks = Collection().from_module(cmake)
kernel_tasks = Collection().from_module(kernel)

collection = Collection().from_module(common)
collection.add_collection(compiler_tasks)
collection.add_collection(board_tasks)
collection.add_collection(admin_tasks)
collection.add_collection(cmake_tasks)
collection.add_collection(kernel_tasks)
