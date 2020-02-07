#!/bin/bash -e

BOARDS="zynqberry jetsontx2 jetsonagx"

BOARDS=$(automate board.board-ids --filter '"default" in [kernel.id for kernel in board.os.kernels]')

for BOARD in $BOARDS; do
    echo "Compile kernel for $BOARD"
    automate  kernel.configure $BOARD default
    automate  kernel.build $BOARD 
    automate  kernel.install $BOARD
done
