"""Custom exceptions for sheriff spider."""


class BookingSpiderError(Exception):
    """Base exception for BookingSpider errors."""


class InvalidResponseError(Exception):
    """Raised if the response content type is invalid."""
