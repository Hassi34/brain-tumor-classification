import argparse
from src.utils.common import read_yaml
from src.cloud_sync import CloudSync
from src.utils.app_logging import get_logger

STAGE = "Load Data"

def get_data():

    logger.info("Loading data from the source...")
    cloud_sync.sync_gcs_to_local_data_dir()
    logger.info("Data has been saved locally")

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    parsed_args = args.parse_args()
    cloud_sync = CloudSync()
    config = read_yaml(parsed_args.config)
    LOGS_FILE_PATH = config['logs']['RUNNING_LOGS_FILE_PATH']
    logger = get_logger(LOGS_FILE_PATH)
    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        get_data()
        #cloud_sync.upload_logs()
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
    except Exception as e:
        cloud_sync.upload_logs()
        logger.exception(e)
        raise e