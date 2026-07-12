import io
import sys

from main import _ensure_utf8_stdout


def test_ensure_utf8_stdout_reconfigures_legacy_codepage_streams(monkeypatch):
    fake_stdout = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    fake_stderr = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", fake_stderr)

    _ensure_utf8_stdout()

    assert sys.stdout.encoding.lower() == "utf-8"
    assert sys.stderr.encoding.lower() == "utf-8"


def test_ensure_utf8_stdout_ignores_streams_without_reconfigure(monkeypatch):
    class NoReconfigureStream:
        pass

    monkeypatch.setattr(sys, "stdout", NoReconfigureStream())

    _ensure_utf8_stdout()  # should not raise
