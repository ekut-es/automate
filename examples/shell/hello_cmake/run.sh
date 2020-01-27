#!/bin/bash -e

BOARDS=$(automate board.board-ids)


for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  cmake.configure $BOARD -s hello
    automate  cmake.build     $BOARD -s hello
    automate  cmake.install   $BOARD -s hello 
    automate  board.lock      $BOARD 
    automate  cmake.deploy    $BOARD -s hello
    automate  board.run       $BOARD ./hello/bin/CMakeHelloWorld 
    automate  board.unlock    $BOARD 
done
