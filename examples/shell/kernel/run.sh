#!/bin/bash -e

if [ -z "$1" ]; then
    BOARDS=$(automate board.board-ids --filter '"default" in [kernel.name for kernel in board.os.kernels]')

else
    if [ "$1" == "-h" ]; then
	echo "usage: ./run.sh <board_name>"
	echo "       Build kernel config default"
	echo "       If no Boardname is given all default configs are built"
	exit 0
    fi
    BOARDS="$1"
fi



for BOARD in $BOARDS; do
    echo "Compile kernel for $BOARD"
    automate  kernel.configure $BOARD default
    automate  kernel.build $BOARD 
    automate  kernel.install $BOARD
done
