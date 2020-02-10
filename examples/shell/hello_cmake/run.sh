#!/bin/bash -e

BOARDS=$(automate board.board-ids)

rm -rf builds

for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  cmake.configure $BOARD -s hello_cmake 
    automate  cmake.build     $BOARD 
    automate  cmake.install   $BOARD
    automate  board.lock      $BOARD
    automate  board.run       $BOARD 'rm -rf ./hello_cmake/'
    automate  cmake.deploy    $BOARD 
    automate  board.run       $BOARD ./hello_cmake/bin/CMakeHelloWorld 
    automate  board.unlock    $BOARD 
done
