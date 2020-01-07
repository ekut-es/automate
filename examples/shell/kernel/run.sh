#!/bin/bash -e

BOARDS="zynqberry jetsontx2 jetsonagx"


for BOARD in $BOARDS; do
    echo "Compile kernel for $BOARD"
    automate  kernel.configure $BOARD default
    automate  kernel.build $BOARD default
#    automate  kernel.install $BOARD default
done
