#!/bin/bash -e

BOARDS=$(automate board.board-ids)
BENCHMARKS="opencv_perf_calib3d  opencv_perf_features2d  opencv_perf_imgproc opencv_perf_stitching opencv_perf_core     opencv_perf_gapi opencv_perf_objdetect  opencv_perf_video opencv_perf_dnn  opencv_perf_imgcodecs   opencv_perf_photo opencv_perf_videoio"

if [ ! -e opencv-4.1.2 ]; then
    wget -c  https://github.com/opencv/opencv/archive/4.1.2.zip
    unzip 4.1.2.zip
fi

if [ ! -e opencv_extra ]; then
    git clone https://github.com/opencv/opencv_extra.git
else
    pushd opencv_extra
    git pull
    popd
fi

for BOARD in $BOARDS; do
    automate board.rsync-to $BOARD opencv_extra/testdata/
done


pushd opencv-4.1.2
for BOARD in $BOARDS; do
    echo "Compile and run for $BOARD"
    # Build all dependencies even if they have been found in sysroot
    # Note the space after -D is unfortunately important
    automate  cmake.configure $BOARD -D OPENCV_FORCE_3RDPARTY_BUILD=1 -D INSTALL_TESTS=1
    automate  cmake.build     $BOARD 
    automate  board.lock      $BOARD 
    automate  cmake.install   $BOARD
    automate  board.run       $BOARD 'source bin/setup_vars_opencv4.sh  && ./bin/opencv_version'

    #Run Benchmarks
    for benchmark in $BENCHMARKS; do
	automate board.run $BOARD "source bin/setup_vars_opencv4.sh  && ./bin/$benchmark"
    done
    
    automate  board.unlock    $BOARD 
done
popd
