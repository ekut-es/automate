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

        assert models[0].num == 0
        assert models[1].num == 1

        assert models[0].isa == "armv7-a"
        assert models[1].isa == "armv7-a"

        assert models[0].uarch == "cortex-a9"
        assert models[1].uarch == "cortex-a9"

        assert models[0].vendor == "arm"
        assert models[1].vendor == "arm"

        assert set([f for f in models[0].extensions]) == set(
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
        assert set([f for f in models[1].extensions]) == set(
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
        assert models[0].isa == ""
        assert models[0].vendor == ""
        assert models[0].uarch == ""

        assert "test_unknown" in models[0].extensions
