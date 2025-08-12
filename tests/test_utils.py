"""Test suite for utility functions."""

from sheriffwebsites.items import BookingItem
from sheriffwebsites.utils import allows_none


def test_allows_none() -> None:
    """Test that we can detect fields that allow None."""
    assert allows_none(BookingItem.model_fields["zipcode"].annotation)
