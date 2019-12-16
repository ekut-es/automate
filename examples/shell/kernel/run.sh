#!/bin/bash -e

BOARD=jetsontx2
CONFIG_OPTIONS="CONFIG_BPF=y CONFIG_PROC_KCORE=y CONFIG_IKCONFIG=y CONFIG_IKCONFIG_PROC=y CONFIG_BPF_JIT=y CONFIG_HAVE_EBPF_JIT=y CONFIG_HW_PERF_EVENTS=y CONFIG_KEXEC=y CONFIG_KEXEC_CORE=y"

config=""
for option in $CONFIG_OPTIONS; do
    config="${config} -c ${option}" 
done

echo "Compile and run for $BOARD"
automate  kernel.configure $BOARD jailhouse $config
#automate  kernel.build $BOARD jailhouse
