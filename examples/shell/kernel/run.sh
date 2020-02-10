#!/bin/bash -e


BOARDS=$(automate board.board-ids --filter '"default" in [kernel.name for kernel in board.os.kernels]')

BOARDS="raspberrypi4b-jh1"


for BOARD in $BOARDS; do
    echo "Compile kernel for $BOARD"
    automate  kernel.configure $BOARD default
    automate  kernel.build $BOARD 
    automate  kernel.install $BOARD
done
