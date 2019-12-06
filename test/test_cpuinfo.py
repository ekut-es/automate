import os
from automate.utils.cpuinfo import _cpuinfo


def test_cpuinfo():

    cpuinfo_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "src/cpuinfo_zynqberry.txt"
    )

    with open(cpuinfo_file) as f:
        text = f.read()
        models = _cpuinfo(text)

        assert len(models) == 2

        assert models[0].id == 0
        assert models[1].id == 1

        assert models[0].isa.value == "armv7-a"
        assert models[1].isa.value == "armv7-a"

        assert models[0].uarch.value == "cortex-a9"
        assert models[1].uarch.value == "cortex-a9"

        assert models[0].vendor.value == "arm"
        assert models[1].vendor.value == "arm"

        assert set([f.value for f in models[0].extensions]) == set(
            [
                "half",
                "thumb",
                "fastmult",
                "vfp",
                "edsp",
                "neon",
                "vfpv3",
                "tls",
                "vfpd32",
            ]
        )
        assert set([f.value for f in models[1].extensions]) == set(
            [
                "half",
                "thumb",
                "fastmult",
                "vfp",
                "edsp",
                "neon",
                "vfpv3",
                "tls",
                "vfpd32",
            ]
        )


def test_unknown():
    cpuinfo_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "src/cpuinfo_unknown.txt"
    )

    with open(cpuinfo_file) as f:
        text = f.read()
        models = _cpuinfo(text)

        assert len(models) == 1
        assert models[0].isa.value == "unknown"
        assert models[0].vendor.value == "unknown"
        assert models[0].uarch.value == "unknown"

        assert "unknown" in [f.value for f in models[0].extensions]
