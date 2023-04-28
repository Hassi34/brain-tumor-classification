
from src.cloud_sync import CloudSync


def download_production_model():

    cloud_sync = CloudSync()
    cloud_sync.download_blessed_model()

if __name__ == '__main__':

    download_production_model()
