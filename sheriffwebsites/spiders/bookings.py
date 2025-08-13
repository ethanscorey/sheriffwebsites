"""A Scrapy Spider for scraping bookings."""

from collections.abc import Iterator, AsyncIterator
from typing import Any

import scrapy

from sheriffwebsites.items import BookingItem
from sheriffwebsites.utils import (
    delist_maybe,
    ensure_json_response,
    get_county_info,
    get_booking_url,
)
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
        """
        bookings = ensure_json_response(response)
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
            return self.get_booking_item(booking, county)
        return scrapy.Request(
            url=get_booking_url(county, booking),
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
        InvalidResponseError
            Raised if the response isn't the correct type.
        """
        response_data = ensure_json_response(response)
        data_key = get_county_info(county, "key")
        person = delist_maybe(response_data[data_key])
        yield self.get_booking_item(person, county)

    @staticmethod
    def get_booking_item(data: dict[str, Any], county: str) -> BookingItem:
        """Create a BookingItem from scraped data.

        Parameters
        ----------
        data : dict[str, Any]
            The scraped data.
        county : str
            The county from which the data was scraped.

        Returns
        -------
        BookingItem
            The booking item.
        """
        return BookingItem(**(data | {"county": county}))
