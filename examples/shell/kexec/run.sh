BOARDS="zynqberry jetsontx2"

for BOARD in $BOARDS; do
automate board.lock $BOARD
cmdline=$(automate board.run $BOARD "cat /proc/cmdline")
echo "Original commandline of $BOARD: $cmdline"
automate board.kexec $BOARD --append="isolcpus=1" --wait
cmdline=$(automate board.run $BOARD "cat /proc/cmdline")
echo "Commandline of $BOARD after kexec $cmdline"
automate board.reboot $BOARD --wait
cmdline=$(automate board.run $BOARD "cat /proc/cmdline")
echo "Commandline of $BOARD after reboot $cmdline"
automate board.unlock $BOARD
echo ""
done
