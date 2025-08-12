"""A Scrapy Spider for scraping bookings."""

from collections.abc import Iterator, AsyncIterator
from typing import Any

import scrapy

from sheriffwebsites.items import BookingItem
from sheriffwebsites.utils import delist_maybe
from sheriffwebsites import settings


class BookingSpider(scrapy.Spider):
    """Scrape booking JSON data from jail rosters built by Lighthouse.

    Attributes
    ----------
    name: str
        The spider name.
    """

    name: str = "sheriffwebsites"

    async def start(self) -> AsyncIterator[scrapy.Request]:
        """Send initial requests to each site.

        Yields
        ------
        scrapy. Request
            The initial requests.
        """
        sites = settings.SHERIFF_SITES
        for county, county_data in sites.items():
            yield scrapy.Request(
                f"{county_data['site']}/dmxConnect/api/Booking/Read2.php",
                callback=self.parse_initial,
                cb_kwargs={"county": county},
            )

    def parse_initial(
        self, response: scrapy.http.Response, county: str
    ) -> Iterator[scrapy.Request | BookingItem]:
        """Parse initial array of booking IDs and send requests for each.

        Parameters
        ----------
        response : scrapy.http.Response
            The initial response.
        county : str
            The county jail being scraped.

        Yields
        ------
        scrapy.Request | BookingItem
            A request for each individual booking, or the booking itself.

        Raises
        ------
        ValueError
            Raised if the response isn't the correct type.
        """
        if not hasattr(response, "json"):
            raise ValueError("Invalid response.")
        bookings = response.json()
        for booking in bookings.get("query", []):
            yield self.get_booking(booking, county)

    def get_booking(
        self, booking: dict[str, Any], county: str
    ) -> scrapy.Request | BookingItem:
        """Return a request for an individual booking record.

        Parameters
        ----------
        booking : dict[str, Any]
            The booking data
        county : str
            The county jail being scraped.

        Returns
        -------
        scrapy.Request | BookingItem
            A request for individual booking data or the booking itself.
        """
        if len(booking.keys()) > 1:
            return BookingItem(**booking | {"county": county})
        site = settings.SHERIFF_SITES[county]["site"]
        booking_key = settings.SHERIFF_SITES[county].get("booking_key", "BookingID")
        booking_param = booking_key.lower()
        booking_id = booking[booking_key]
        return scrapy.Request(
            url=f"{site}/dmxConnect/api/Booking/getbookie.php?{booking_param}={booking_id}",
            callback=self.parse_booking,
            cb_kwargs={"county": county},
        )

    def parse_booking(
        self, response: scrapy.http.Response, county: str
    ) -> Iterator[BookingItem]:
        """Parse an individual booking.

        Parameters
        ----------
        response : scrapy.http.Response
            The initial response.
        county : str
            The county jail being scraped.

        Yields
        ------
        BookingItem
            The parsed booking.

        Raises
        ------
        ValueError
            Raised if the response isn't the correct type.
        """
        if not hasattr(response, "json"):
            raise ValueError("Invalid response.")
        data_key = settings.SHERIFF_SITES[county]["key"]
        person = delist_maybe(response.json()[data_key]) | {"county": county}
        yield BookingItem(**person)
