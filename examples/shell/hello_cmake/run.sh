#!/bin/bash -e

BOARDS=$(automate board.board-ids)


for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  cmake.configure $BOARD -s hello
    automate  cmake.build $BOARD 
    automate  board.lock       $BOARD 
    automate  cmake.install $BOARD
    automate  cmake.deploy  $BOARD
    automate  board.run        $BOARD ./bin/CMakeHelloWorld 
    automate  board.unlock     $BOARD 
done
