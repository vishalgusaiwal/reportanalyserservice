import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from urllib.parse import urlparse

load_dotenv()

class AzureBlobDownloader:
    def __init__(self):
        self.connectionString = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.containerName = os.getenv("AZURE_CONTAINER_NAME")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connectionString)

    def download_blob(self, blob_url: str, download_path: str) -> None:
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        parsed_url = urlparse(blob_url)
        blob_name = parsed_url.path.split('/',2)[-1]
        print(self.containerName, blob_name)
        blob_client = self.blob_service_client.get_blob_client(container=self.containerName, blob=blob_name)

        local_path = download_path + "/" + blob_name
        print(local_path)
        with open(local_path, "wb") as f:
            blob_data = blob_client.download_blob()
            f.write(blob_data.readall())

        return local_path