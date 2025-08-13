"""Utility functions for the scraper."""

from types import UnionType, NoneType
from typing import Any, TypeVar, Union, get_args, get_origin, overload

import scrapy

from .exceptions import InvalidResponseError
from .settings import SHERIFF_SITES

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


def get_booking_url(county: str, booking: dict[str, Any]) -> str:
    """Get the URL for the specific booking.

    Parameters
    ----------
    county : str
        The booking county.
    booking : dict[str, Any]
        The booking data.

    Returns
    -------
    str
        The booking URL.
    """
    site = get_county_info(county, "site")
    booking_key = get_county_info(county, "booking_key", "BookingID")
    booking_id = booking[booking_key]
    booking_param = booking_key.lower()
    return f"{site}/dmxConnect/api/Booking/getbookie.php?{booking_param}={booking_id}"


def get_county_info(county: str, key: str, default: Any = None) -> Any:
    """Get info for a specific county.

    Parameters
    ----------
    county : str
        The county of interest.
    key : str
        The key for the data of interest.
    default: Any
        The default value if not defined.

    Returns
    -------
    Any
        The data of interest.
    """
    return SHERIFF_SITES[county].get(key, default)


def ensure_json_response(response: scrapy.http.Response) -> Any:
    """Ensure response has JSON data and return it.

    Parameters
    ----------
    response : scrapy.http.Reponse
        The scrapy response.

    Returns
    -------
    Any
        The JSON data.

    Raises
    ------
    InvalidResponseError
    """
    if not hasattr(response, "json"):
        raise InvalidResponseError
    return response.json()
