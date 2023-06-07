import fabric
import invoke
import pytest

import automate


def do_nothing_func(*args, **kwars):
    pass


def return_true_func(*args, **kwargs):
    pass


@pytest.fixture
def monkeypatch_state(monkeypatch):
    """This fixture disables all methods that 
       modify global state"""

    monkeypatch.setattr(fabric.Connection, "run", do_nothing_func)
    monkeypatch.setattr(fabric.Connection, "sudo", do_nothing_func)
    monkeypatch.setattr(fabric.Connection, "is_connected", return_true_func)
    monkeypatch.setattr(invoke.Context, "run", do_nothing_func)
    monkeypatch.setattr(invoke.Context, "sudo", do_nothing_func)
    monkeypatch.setattr(automate.AutomateContext, "run", do_nothing_func)
    monkeypatch.setattr(automate.AutomateContext, "sudo", do_nothing_func)
    monkeypatch.setattr(automate.AutomateContext, "sudo", do_nothing_func)
    monkeypatch.setattr(
        automate.AutomateContext, "_setup_database", do_nothing_func
    )
    monkeypatch.setattr(
        automate.AutomateContext, "_setup_forwards", do_nothing_func
    )
