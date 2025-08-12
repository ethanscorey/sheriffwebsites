"""Tests for validators."""

import datetime as dt

import pytest
from pydantic import ValidationError
from sheriffwebsites.validators import validate_state, soft_validate, convert_date


def test_validate_state() -> None:
    """Test that we can validate a state field."""
    assert validate_state("MD") == "MD"
    with pytest.raises(ValueError):
        validate_state("Germany")


def test_soft_validate() -> None:
    """Test soft validation."""

    def handler(value: str) -> str:
        if value == "bar":
            raise ValidationError("missing", [])
        return value.upper()

    assert soft_validate("foo", handler) == "FOO"
    assert soft_validate("bar", handler) is None


def test_convert_date() -> None:
    """Test date conversion."""
    assert convert_date("09/06/1993") == dt.datetime(1993, 9, 6)
