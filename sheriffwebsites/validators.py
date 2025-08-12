"""Pydantic validators for parsing booking information."""

from collections.abc import Callable
import datetime as dt
from typing import TypeVar
import re

from pydantic import ValidationError
from us.states import lookup

X = TypeVar("X")
Y = TypeVar("Y")


def validate_state(state_candidate: str) -> str:
    """Validate string as a state.

    Parameters
    ----------
    state_candidate : str
        The string that might be a state.

    Returns
    -------
    str
        The state abbreviation for the matching state.

    Raises
    ------
    ValueError
        Raised if the string is not a valid state.
    """
    state = lookup(state_candidate)
    if state is not None:
        return state.abbr
    raise ValueError(f"{state_candidate} is not a valid state name.")


def soft_validate(value: X, handler: Callable[[X], Y]) -> Y | None:
    """Return None if validation fails."""
    try:
        return handler(value)
    except ValidationError:
        return None


def convert_date(value: str | dt.datetime) -> dt.datetime | str:
    """Convert supported date formats.

    Parameters
    ----------
    value : str | dt.datetime
        The date string to convert (or a datetime).

    Returns
    -------
    dt.datetime | str
        The converted date, or the string if not converted.
    """
    if isinstance(value, dt.datetime):
        return value
    if re.match(r"\d{2}/\d{2}/\d{4}", value):
        return dt.datetime.strptime(value, "%m/%d/%Y")
    return value
