from graphdatascience.session import SessionMemory


def test_all_values() -> None:
    print(SessionMemory.all_values())
    assert len(SessionMemory.all_values()) == 11
    for e in SessionMemory.all_values():
        assert e.endswith("GB")
