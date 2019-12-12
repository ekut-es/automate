#!/bin/bash -e

BOARDS=$(automate board.board-ids)


for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  compiler.compile $BOARD -f hello.c -o hello
    automate  board.lock       $BOARD 
    automate  board.put        $BOARD build-$BOARD/hello
    automate  board.run        $BOARD ./hello 
    automate  board.unlock     $BOARD 
done
