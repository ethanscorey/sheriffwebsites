"""A Scrapy Spider for scraping bookings."""

from collections.abc import Iterator, AsyncIterator
from typing import Any, cast

from pydantic import ValidationError
import scrapy

from sheriffwebsites.items import BookingItem
from sheriffwebsites.utils import (
    ensure_json_response,
    get_booking_url,
    get_county_info,
    stringify_dict,
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

    def request_query(
        self, county: str, formdata: None | dict[str, Any] = None
    ) -> scrapy.FormRequest:
        """Make a query request with the provided form data.

        Parameters
        ----------
        county : str
            The county to query.
        formdata : None | dict[str, Any]
            The current form data.

        Returns
        -------
        scrapy.FormRequest
            A new request.
        """
        formdata = formdata or {}
        root_site = get_county_info(county, "site")
        api_endpoint = get_county_info(
            county, "read_endpoint", "dmxConnect/api/Booking/Read.php"
        )
        limit = get_county_info(county, "limit", 100)
        formdata.update({"limit": limit})
        return scrapy.FormRequest(
            f"{root_site}/{api_endpoint}",
            callback=self.parse_results,
            cb_kwargs={"county": county},
            formdata=stringify_dict(formdata),
        )

    async def start(self) -> AsyncIterator[scrapy.Request]:
        """Send initial requests to each site.

        Yields
        ------
        scrapy. Request
            The initial requests.
        """
        for county in settings.SHERIFF_SITES:
            yield self.request_query(county)

    def parse_results(
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
        results = self.get_results(response, county)
        offset = results["offset"]
        total = results["total"]
        limit = results["limit"]
        for booking in results["data"]:
            try:
                yield self.get_booking_item(booking, county)
            except ValidationError:
                yield self.request_booking(booking, county)
        if offset + limit <= total:
            yield self.request_query(county, {"offset": offset + limit})

    def request_booking(self, booking: dict[str, Any], county: str) -> scrapy.Request:
        """Request an individual booking.

        Parameters
        ----------
        booking : dict[str, Any]
            The booking data
        county : str
            The county jail being scraped.

        Returns
        -------
        scrapy.Request
            A request for the individual booking.
        """
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
    def get_results(response: scrapy.http.Response, county: str) -> dict[str, Any]:
        """Get the query results from the response body.

        Parameters
        ----------
        response : scrapy.http.Response
            The initial response.
        county : str
            The county jail being scraped.

        Returns
        -------
        dict[str, Any]
            The results dictionary.
        """
        json_response = ensure_json_response(response)
        results_key = get_county_info(county, "results_key", "bookings")
        return cast(dict[str, Any], json_response[results_key])

    def get_booking_item(self, data: dict[str, Any], county: str) -> BookingItem:
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
