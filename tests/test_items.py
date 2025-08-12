"""Test suite for items."""

import pytest
from sheriffwebsites.items import BookingItem


@pytest.fixture
def booking_item() -> BookingItem:
    """Create a test BookingItem."""
    test_data = {
        "BookingID": "13826",
        "InmateID": "40730",
        "BookingNum": "25-0048",
        "BookingDate": "2025-01-22T02:44:00",
        "ReleaseDate": "",
        "heldfor": "",
        "FullName": "TESTLAST, TESTMIDDLE TESTFIRST",
        "FName": "TESTFIRST",
        "MName": "TESTMIDDLE",
        "LName": "TESTLAST",
        "Sex": "M",
        "Race": "W",
        "Classification": "Minimum Security",
        "Pic": "testpic.bmp",
        "Address": "PO BOX 502",
        "City": "EAKLY",
        "State": "OK",
        "Zip": "730  ",
        "Charges": "DRIVING WHILE LICENSE SUSPENDED (DUS) OR REVOKED (DUR)",
        "dob": "01/01/1976",
    }
    return BookingItem(**(test_data | {"county": "Caddo"}))


def test_age(booking_item: BookingItem) -> None:
    """Test that we can get the person's age."""
    assert booking_item.age >= 49


def test_full_name(booking_item: BookingItem) -> None:
    """Test that we can get the person's full name."""
    assert booking_item.full_name == "TESTFIRST TESTMIDDLE TESTLAST"
    booking_item.middle_name = None
    assert booking_item.full_name == "TESTFIRST TESTLAST"


def test_mailing_address(booking_item: BookingItem) -> None:
    """Test that we can get the person's full address."""
    assert booking_item.mailing_address == "PO BOX 502\nEAKLY, OK"
