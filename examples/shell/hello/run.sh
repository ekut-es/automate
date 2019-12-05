#!/bin/bash -e

BOARD=jetsonagx

automate  compiler.compile $BOARD -f hello.c -o hello
automate  board.lock       $BOARD 
automate  board.put        $BOARD build-$BOARD/hello
automate  board.run        $BOARD ./hello 
automate  board.unlock     $BOARD 
