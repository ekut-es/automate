""" Unit tests for cross compiler abstration
"""

import os
from pathlib import Path

from pytest import yield_fixture

import automate.model.common
from automate.config import AutomateConfig
from automate.context import AutomateContext

root_path = os.path.dirname(os.path.abspath(__file__))
metadata_path = os.path.join(root_path, "src", "metadata")


@yield_fixture()
def zynqberry_cc():
    """Test fixture for zynqberry cross compiler"""

    config = AutomateConfig()
    config.automate.metadata = str(metadata_path)
    context = AutomateContext(config)

    board = context.board("zynqberry")
    assert board.id == "zynqberry"
    return board.compiler()

    raise Exception("Could not find zynqberry")


def test_zynqberry_cc_properties(zynqberry_cc):
    cc = zynqberry_cc
    assert cc.board.id == "zynqberry"
    assert len(cc.triples) == 1
    assert cc.version == "7.4.1"
    assert cc.multiarch == True
    assert cc.bin_path == Path(
        "/afs/wsi/es/tools/arm/gcc-linaro-7.4.1-2019.02-x86_64_arm-linux-gnueabihf/bin"
    )
    assert cc.prefix == "arm-linux-gnueabihf-"
    assert cc.cc == "arm-linux-gnueabihf-gcc"
    assert cc.cxx == "arm-linux-gnueabihf-g++"
    assert cc.asm == "arm-linux-gnueabihf-as"
    assert cc.ld == "arm-linux-gnueabihf-ld"
    assert cc.toolchain == automate.model.common.Toolchain.GCC
    assert cc.id == "aarch32hf-gcc74"
