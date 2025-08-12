"""Pydantic validators for parsing booking information."""

from collections.abc import Callable
from typing import TypeVar

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
