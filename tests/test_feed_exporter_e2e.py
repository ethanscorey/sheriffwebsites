"""E2E test for Azure feed storage backend."""

import os
import uuid

import pytest
import pytest_twisted
from azure.storage.blob import BlobServiceClient
from scrapy.settings import Settings
from scrapy.crawler import Crawler
from scrapy.extensions.feedexport import FeedExporter

from sheriffwebsites.feedstorages.azure_blob import AzureBlobFeedStorage


AZURITE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
    "K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    "QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint="
    "http://127.0.0.1:10002/devstoreaccount1;"
)


@pytest.mark.e2e
@pytest_twisted.inlineCallbacks
def test_feed_exporter_writes_csv(monkeypatch, mocker):
    """Test that the feed exporter writes to blob storage."""
    mock_spider = mocker.Mock()
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", AZURITE_CONNECTION_STRING)
    container = f"test-container"
    blob_path = f"exports/{uuid.uuid4().hex}/items.csv"
    feed_uri = f"az://{container}/{blob_path}"
    settings = Settings(
        {
            "FEED_STORAGES": {
                "az": "sheriffwebsites.feedstorages.azure_blob.AzureBlobFeedStorage"
            },
            "FEEDS": {
                feed_uri: {
                    "format": "csv",
                    "encoding": "utf-8",
                    "fields": ["id", "name"],
                }
            },
            "FEED_EXPORT_BATCH_ITEM_COUNT": 0,
        }
    )

    crawler = Crawler(spidercls=mock_spider, settings=settings)
    mock_spider.crawler = crawler
    exporter = FeedExporter.from_crawler(crawler)
    exporter.open_spider(spider=mock_spider)
    print("here")

    for item in [
        {"id": 1, "name": "a"},
        {"id": 2, "name": "b"},
    ]:
        exporter.item_scraped(item, spider=mock_spider)
    yield exporter.close_spider(spider=mock_spider)
    print("here!")
    service = BlobServiceClient.from_connection_string(AZURITE_CONNECTION_STRING)
    blob = service.get_blob_client(container=container, blob=blob_path)
    assert blob.exists(), "Blob not found in Azurite."

    data = blob.download_blob().readall()
    text = data.decode("utf-8")

    assert "id,name" in text
    assert "1,a" in text
    assert "2,b" in text
