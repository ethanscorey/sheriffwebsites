"""Test Azure feed storage."""

import io
import types


from sheriffwebsites.feedstorages.azure_blob import AzureBlobFeedStorage


class StubBlob:
    def __init__(self):
        self.uploaded = None
        self.overwrite = None
        self.content_type = None
        self.container_created = False
        self._container_client = types.SimpleNamespace(
            create_container=self.create_container
        )
        self._blob = types.SimpleNamespace(
            upload_blob=self.upload_blob
        )

    def get_container_client(self, container: str):
        return self._container_client

    def get_blob_client(self, container: str, blob_path: str):
        return self._blob

    def create_container(self, **kwargs):
        self.container_created = True

    def upload_blob(self, data, overwrite, content_settings):
        self.uploaded = data
        self.overwrite = overwrite
        self.content_type = content_settings.content_type


def test_store_uploads_csv(monkeypatch):
    """Test that we can upload a CSV to blob storage."""
    storage = AzureBlobFeedStorage(
        "az://myc/exports/tests.csv",
        feed_options={"account_url": "https://acct.blob.core.windows.net"},
    )
    stub = StubBlob()
    monkeypatch.setattr(storage, "_get_service", lambda: stub)

    dummy_file = io.BytesIO(b"col1,col2\n1,2\n")
    storage._store_in_thread(dummy_file)

    assert stub.container_created is True
    assert stub.uploaded == b"col1,col2\n1,2\n"
    assert stub.overwrite is True
    assert stub.content_type.startswith("text/csv")
