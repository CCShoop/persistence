import os
import threading

from persistence import Persistence


def test_write_then_read_round_trips(tmp_path):
    persist = Persistence(str(tmp_path / "data.json"))
    persist.write({"events": [{"name": "test"}]})
    assert persist.read() == {"events": [{"name": "test"}]}


def test_read_missing_file_returns_none(tmp_path):
    assert Persistence(str(tmp_path / "missing.json")).read() is None


def test_write_default(tmp_path):
    persist = Persistence(str(tmp_path / "data.json"))
    persist.write()
    assert persist.read() == {}


def test_write_overwrites_previous_contents(tmp_path):
    persist = Persistence(str(tmp_path / "data.json"))
    persist.write({"events": [1, 2, 3]})
    persist.write({"events": []})
    assert persist.read() == {"events": []}


def test_write_handles_non_ascii(tmp_path):
    persist = Persistence(str(tmp_path / "data.json"))
    persist.write({"name": "アニメ"})
    assert persist.read() == {"name": "アニメ"}


def test_paused_skips_read_and_write(tmp_path):
    persist = Persistence(str(tmp_path / "data.json"))
    persist.write({"saved": True})
    persist.pause()
    persist.write({"saved": False})
    assert persist.read() is None
    persist.resume()
    assert persist.read() == {"saved": True}


def test_write_leaves_no_temp_file(tmp_path):
    persist = Persistence(str(tmp_path / "data.json"))
    persist.write({"events": []})
    assert [path.name for path in tmp_path.iterdir()] == ["data.json"]


def test_failed_write_keeps_previous_file(tmp_path, monkeypatch):
    persist = Persistence(str(tmp_path / "data.json"))
    persist.write({"saved": True})

    def crash(*args):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", crash)
    try:
        persist.write({"saved": False})
    except OSError:
        pass
    monkeypatch.undo()
    assert persist.read() == {"saved": True}


def test_unchanged_data_is_not_rewritten(tmp_path):
    path = tmp_path / "data.json"
    persist = Persistence(str(path))
    persist.write({"a": 1})
    path.write_text("{}")
    persist.write({"a": 1})
    assert persist.read() == {}
    persist.write({"a": 2})
    assert persist.read() == {"a": 2}


def test_serializes_concurrent_access(tmp_path):
    persist = Persistence(str(tmp_path / "data.json"))
    errors = []

    def worker(i):
        try:
            for j in range(50):
                persist.write({"worker": i, "n": j})
                assert persist.read()["worker"] in range(8)
        except Exception as e:  # pragma: no cover
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []


def test_quarantine_moves_unreadable_file_aside(tmp_path):
    path = tmp_path / "data.json"
    path.write_text("{not json")
    persist = Persistence(str(path))
    backup = persist.quarantine()
    assert not path.exists()
    assert open(backup).read() == "{not json"
    assert backup.startswith(str(path) + ".corrupt-")


def test_quarantine_without_file_returns_none(tmp_path):
    assert Persistence(str(tmp_path / "data.json")).quarantine() is None


def test_write_after_quarantine_is_not_skipped_as_unchanged(tmp_path):
    persist = Persistence(str(tmp_path / "data.json"))
    persist.write({"a": 1})
    persist.quarantine()
    persist.write({"a": 1})
    assert persist.read() == {"a": 1}
