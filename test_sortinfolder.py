import subprocess
import sys
from datetime import date, datetime

import pytest

from sortinfolder import rotate_last_actioned_on


def test_help_shows_usage_and_examples():
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
    assert "usage: sortimages" in output
    assert "options:" in output
    assert "Examples:" in output


def test_rotate_last_actioned_on_sets_date_and_returns_record():
    record = {"last_actioned_on": date(2020, 1, 2)}
    result = rotate_last_actioned_on(record)
    assert result is record
    assert record["last_actioned_on"] == date.today()
    assert isinstance(record["last_actioned_on"], date)


def test_rotate_last_actioned_on_normalizes_datetime():
    record = {"last_actioned_on": datetime(2019, 5, 17, 23, 30)}
    result = rotate_last_actioned_on(record)
    assert result is record
    assert record["last_actioned_on"] == date.today()
    assert isinstance(record["last_actioned_on"], date)


def test_rotate_last_actioned_on_parses_iso_string():
    record = {"last_actioned_on": "2024-01-31"}
    result = rotate_last_actioned_on(record)
    assert result is record
    assert record["last_actioned_on"] == date.today()
    assert isinstance(record["last_actioned_on"], date)


def test_rotate_last_actioned_on_rejects_non_dict():
    with pytest.raises(TypeError):
        rotate_last_actioned_on(["last_actioned_on"])
    with pytest.raises(TypeError):
        rotate_last_actioned_on(None)


def test_rotate_last_actioned_on_requires_last_actioned_on_key():
    record = {"other_key": "value"}
    with pytest.raises(ValueError):
        rotate_last_actioned_on(record)
    assert record == {"other_key": "value"}


def test_rotate_last_actioned_on_rejects_invalid_existing_value():
    with pytest.raises(TypeError):
        rotate_last_actioned_on({"last_actioned_on": 7})
    with pytest.raises(TypeError):
        rotate_last_actioned_on({"last_actioned_on": "31.01.2024"})
