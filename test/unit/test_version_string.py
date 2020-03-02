from pydantic import BaseModel

from automate.model.common import VersionString


def test_version_string():

    v1 = VersionString("1.0")
    v8 = VersionString("8.0")
    v810 = VersionString("8.1.0")
    v10 = VersionString("10.0")

    assert v1 < v8 < v810 < v10
    assert v1 <= v8 <= v810 <= v10
    assert v10 > v810 > v8 > v1
    assert v10 >= v810 >= v8 >= v1
    assert str(v10) < str(v8)


def test_version_string_pydantic():
    class TestModel(BaseModel):
        version: VersionString

    m8 = TestModel(version="8.0")
    m10 = TestModel(version="10.0")

    assert isinstance(m8.version, VersionString)
    assert isinstance(m10.version, VersionString)

    assert m8.version < m10.version
