import os

from automate import AutomateConfig, AutomateContext
from monkeypatch_state import monkeypatch_state

root_path = os.path.dirname(os.path.abspath(__file__))
metadata_path = os.path.join(root_path, "src", "metadata")


def test_monkeypatch_state(monkeypatch_state):
    config = AutomateConfig(lazy=True)
    config.automate.metadata = str(metadata_path)
    context = AutomateContext(config)

    assert context.run("definitely not existing command") is None
