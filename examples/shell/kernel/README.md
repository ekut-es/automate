# Build default kernels

This script usues automate board.board-ids  with --filter option
to filter for all boards with a kernel configuration called "default". 

It the builds the corresponding kernel configuration and updates the kernel 
build cache in ${boardroot} .

