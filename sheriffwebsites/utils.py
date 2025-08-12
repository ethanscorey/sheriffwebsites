"""Utility functions for the scraper."""

from types import UnionType, NoneType
from typing import Any, Union, get_args, get_origin


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
