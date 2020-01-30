#!/bin/bash -e

BOARDS=$(automate board.board-ids)


for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  cmake.configure $BOARD -s hello_cmake
    automate  cmake.build     $BOARD -s hello_cmake
    automate  cmake.install   $BOARD -s hello_cmake
    automate  board.lock      $BOARD 
    automate  cmake.deploy    $BOARD -s hello_cmake
    automate  board.run       $BOARD ./hello_cmake/bin/CMakeHelloWorld 
    automate  board.unlock    $BOARD 
done
