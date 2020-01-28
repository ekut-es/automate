#!/bin/bash -e

BOARDS=$(automate board.board-ids)


for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  make.configure   $BOARD -s hello_make 
    automate  make.build       $BOARD 
    automate  board.lock       $BOARD 
    automate  make.deploy      $BOARD
    automate  board.run        $BOARD ./hello_make/hello 
    automate  board.unlock     $BOARD 
done