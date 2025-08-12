"""A Scrapy Spider for scraping bookings."""

from collections.abc import Iterator

import scrapy

from sheriffwebsites.items import BookingItem


class BookingSpider(scrapy.Spider):
    """Scrape booking JSON data from jail rosters built by Lighthouse.

    Attributes
    ----------
    name: str
        The spider name.
    start_urls: list[str]
        The starting URLs for the scrape.
    """

    name: str = "sheriffwebsites"
    start_urls: list[str] = [
        "https://caddocountysheriff.com/dmxConnect/api/Booking/Read2.php?filter="
    ]

    def parse(self, response: scrapy.http.Response) -> Iterator[scrapy.Request]:
        """Parse initial array of booking IDs and send requests for each.

        Parameters
        ----------
        response : scrapy.http.Response
            The initial response.

        Yields
        ------
        scrapy.Request
            A request for each individual booking.

        Raises
        ------
        ValueError
            Raised if the response isn't the correct type.
        """
        if not hasattr(response, "json"):
            raise ValueError("Invalid response.")
        bookings = response.json()
        for booking in bookings.get("query", []):
            yield self.get_booking(booking["BookingID"])

    def get_booking(self, booking: str) -> scrapy.Request:
        """Return a request for an individual booking record.

        Parameters
        ----------
        booking : str
            The booking ID

        Returns
        -------
        scrapy.Request
            A request for individual booking data.
        """
        return scrapy.Request(
            url=f"https://caddocountysheriff.com/dmxConnect/api/Booking/getbookie.php?bookingid={booking}",
            callback=self.parse_booking,
        )

    def parse_booking(self, response: scrapy.http.Response) -> Iterator[BookingItem]:
        """Parse an individual booking.

        Parameters
        ----------
        response : scrapy.http.Response
            The initial response.

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
        person = response.json()["bookie"][0]
        self.logger.info(person)
        yield BookingItem(**person)
