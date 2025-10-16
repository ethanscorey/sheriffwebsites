"""Store scraped items as a CSV in Azure blob storage."""

import os
from typing import Any
from urllib.parse import urlparse

from scrapy.extensions.feedexport import BlockingFeedStorage


class AzureBlobFeedStorage(BlockingFeedStorage):
    """Store items in Azure blob storage.

    Parameters
    ----------
    uri : str
        The URI for the feed.
    feed_options : dict[str, Any] | None
        Feed-specific options, if any.

    Raises
    ------
    ValueError
        Raised if the URI is not an Azure URI.
    RuntimeError
        Raised if no account URL provided.
    """

    def __init__(self, uri: str, *, feed_options: dict[str, Any] | None = None):
        parsed = urlparse(uri)

        if parsed.scheme != "az":
            raise ValueError("Unsupported URI scheme.")

        self.container = parsed.netloc
        self.blob_path = parsed.path.lstrip("/")
        self.feed_options = feed_options or {}
        self._account_url = self.feed_options.get("account_url") or os.getenv(
            "AZURE_STORAGE_ACCOUNT_URL"
        )
        self._connection_string = self.feed_options.get("connection_string") or os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        if not self._account_url and not self._connection_string:
            raise RuntimeError("account_url or connection_string are required for MSI auth")

    def _get_service(self):
        """Get the Azure Blob Service client."""
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient

        credential = DefaultAzureCredential()
        if self._connection_string:
            return BlobServiceClient.from_connection_string(self._connection_string)
        return BlobServiceClient(account_url=self._account_url, credential=credential)

    def _store_in_thread(self, file):
        file.seek(0)
        data = file.read()
        from azure.storage.blob import ContentSettings

        content_settings = ContentSettings(content_type="text/csv; charset=utf-8")
        service = self._get_service()
        try:
            service.get_container_client(self.container).create_container()
        except:
            pass
        blob = service.get_blob_client(self.container, self.blob_path)
        blob.upload_blob(data, overwrite=True, content_settings=content_settings)
