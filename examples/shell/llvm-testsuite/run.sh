#!/bin/bash -e

BOARDS=$(automate board.board-ids)

if [ ! -e llvm-test-suite ] ; then
    git clone https://github.com/llvm/llvm-test-suite.git
fi

pushd llvm-test-suite
git checkout master
git reset --hard
git pull
git apply ../patch/gcc_compat.patch
popd


pushd llvm-test-suite
for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  cmake.configure $BOARD 
    automate  cmake.build     $BOARD 
    automate  board.lock      $BOARD 
    #automate  cmake.install   $BOARD
    #automate  board.run       $BOARD ./bin/CMakeHelloWorld 
    automate  board.unlock    $BOARD 
done
popd
