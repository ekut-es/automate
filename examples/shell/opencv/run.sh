#!/bin/bash -e

BOARDS=$(automate board.board-ids)


rm -rf opencv-4.1.2/
wget -c  https://github.com/opencv/opencv/archive/4.1.2.zip
unzip 4.1.2.zip
pushd opencv-4.1.2
for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    automate  cmake.configure $BOARD -D BUILD_PNG=1 -D BUILD_ZLIB=1 -D BUILD_JPEG=1 -D BUILD_TIFF=1
    automate  cmake.build     $BOARD 
    automate  board.lock      $BOARD 
    automate  cmake.install   $BOARD
    automate  board.run       $BOARD 'source bin/setup_vars_opencv4.sh  && ./bin/opencv_version'
    automate  board.unlock    $BOARD 
done
popd
