#!/bin/bash -e

if [ -z "$1" ]
then
    BOARDS=$(automate board.board-ids)
else
    BOARDS=$1
fi

for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  make.configure   $BOARD -s perf_events  
    automate  make.build       $BOARD 
    automate  board.lock       $BOARD 
    automate  make.deploy      $BOARD
    automate  board.run        $BOARD "sudo ./perf_events/perf_events"
    automate  board.unlock     $BOARD 
done


