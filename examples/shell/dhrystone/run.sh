#!/bin/bash -e

BOARDS=$(automate board.board-ids)


for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  compiler.compile $BOARD -f dhry_1.c -f dhry_2.c -o dhry
    automate  board.lock       $BOARD 
    automate  board.put        $BOARD builds/$BOARD/dhry
    automate  board.run        $BOARD ./dhry
    automate  board.unlock     $BOARD 
done
