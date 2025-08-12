"""Test suite for utility functions."""

from sheriffwebsites.items import BookingItem
from sheriffwebsites.utils import allows_none, delist_maybe


def test_allows_none() -> None:
    """Test that we can detect fields that allow None."""
    assert allows_none(BookingItem.model_fields["zipcode"].annotation)


def test_delist_maybe() -> None:
    """Test that we can delist things."""
    assert delist_maybe(["foo"]) == "foo"
    assert delist_maybe(0) == 0
