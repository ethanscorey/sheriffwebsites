"""Integration test for Azure feed exporter."""

import asyncio
import os
import types

import pytest_twisted
from scrapy.settings import Settings
from scrapy.crawler import Crawler
from scrapy.extensions.feedexport import FeedExporter

from sheriffwebsites.feedstorages.azure_blob import AzureBlobFeedStorage


class StubBlob:
    def __init__(self):
        self.uploads = []
        self.container_created = False
        self._container_client = types.SimpleNamespace(
            create_container=self.create_container
        )
        self._blob = types.SimpleNamespace(upload_blob=self.upload_blob)

    def get_container_client(self, container: str):
        return self._container_client

    def get_blob_client(self, container: str, blob_path: str):
        return self._blob

    def create_container(self, **kwargs):
        self.container_created = True

    def upload_blob(self, data, overwrite, content_settings):
        self.uploads.append((data, overwrite, content_settings))


@pytest_twisted.inlineCallbacks
def test_feed_exporter_writes_csv(monkeypatch, mocker):
    """Test that the feed exporter writes to blob storage."""
    stub = StubBlob()
    mock_spider = mocker.Mock()
    monkeypatch.setattr(AzureBlobFeedStorage, "_get_service", lambda self: stub)
    os.environ["AZURE_STORAGE_ACCOUNT_URL"] = "https://myaccounturl.com"

    settings = Settings(
        {
            "FEED_STORAGES": {
                "az": "sheriffwebsites.feedstorages.azure_blob.AzureBlobFeedStorage"
            },
            "FEEDS": {
                "az://myc/exports/test.csv": {
                    "format": "csv",
                    "encoding": "utf-8",
                    "fields": ["id", "name"],
                }
            },
        }
    )

    crawler = Crawler(spidercls=mock_spider, settings=settings)
    mock_spider.crawler = crawler
    exporter = FeedExporter.from_crawler(crawler)
    exporter.open_spider(spider=mock_spider)

    for item in [
        {"id": 1, "name": "a"},
        {"id": 2, "name": "b"},
    ]:
        exporter.item_scraped(item, spider=mock_spider)
    yield exporter.close_spider(spider=mock_spider)
    (data, overwrite, content_settings) = stub.uploads[0]
    assert b"id,name" in data and b"1,a" in data and b"2,b" in data
    assert overwrite is True
    assert content_settings.content_type.startswith("text/csv")
