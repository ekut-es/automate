from invoke import Collection

from ..database import database_enabled
from . import admin, board, cmake, common, compiler, database, kernel, make

compiler_tasks = Collection().from_module(compiler)
board_tasks = Collection().from_module(board)
admin_tasks = Collection().from_module(admin)
cmake_tasks = Collection().from_module(cmake)
kernel_tasks = Collection().from_module(kernel)
make_tasks = Collection().from_module(make)
database_tasks = Collection().from_module(database)

collection = Collection().from_module(common)
collection.add_collection(compiler_tasks)
collection.add_collection(board_tasks)
collection.add_collection(admin_tasks)
collection.add_collection(cmake_tasks)
collection.add_collection(kernel_tasks)
collection.add_collection(make_tasks)

if database_enabled():
    collection.add_collection(database_tasks)
