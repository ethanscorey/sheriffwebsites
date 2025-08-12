"""Utility functions for the scraper."""

from types import UnionType, NoneType
from typing import Any, TypeVar, Union, get_args, get_origin, overload

X = TypeVar("X")
Y = TypeVar("Y")


def allows_none(annotation: Any) -> bool:
    """Determine if an annotation allows the NoneType.

    Parameters
    ----------
    annotation : Any
        A type annotation.

    Returns
    -------
    bool
        Whether the annotation allows for NoneType.
    """
    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        return NoneType in get_args(annotation)
    return annotation is None


@overload
def delist_maybe(value: list[X]) -> X: ...
@overload
def delist_maybe(value: Y) -> Y: ...
def delist_maybe(value: list[X] | Y) -> X | Y:
    """If the value is wrapped in a list, delist it.

    Parameters
    ----------
    value : list[X] | Y
        A value that might be wrapped in a list.

    Returns
    -------
    X | Y
        The unwrapped value.
    """
    if isinstance(value, list):
        return value[0]
    return value
