import os
from src.utils.common import read_yaml
from src.utils.gcp_bucket import BucketGCP

config = read_yaml("configs/config.yaml")
params = read_yaml("params.yaml")

LOCAL_DATA_DIR = config['local_data']['DATA_DIR']
BUCKET_NAME = config['gcs_config']['BUCKET_NAME']
GCS_DATA_DIR = config['gcs_config']['DATA_DIR']

GS_ARTIFACTS = config['gcs_config']['ARTIFACTS']
GS_UNTRAINED_MODEL = config['gcs_config']['UNTRAINED_MODEL_FILE_PATH']
GS_TRAINED_MODEL = config['gcs_config']['TRAINED_MODEL_FILE_PATH']
GS_BLESSED_MODEL = config['gcs_config']['BLESSED_MODEL_FILE_PATH']
GS_LOGS_DIR = config['gcs_config']['LOGS_DIR']
GS_LOGS_FILE_PATH = config['gcs_config']['LOGS_FILE_PATH']
GS_TENSORBOARD_ROOT_LOGS_DIR = config['gcs_config']['TENSORBOARD_ROOT_LOGS_DIR'] 
GS_MODEL_EVAL_DIR = config['gcs_config']['MODEL_EVAL_DIR']
GS_CHECKPOINTS_DIR = config['gcs_config']['CHECKPOINTS_DIR']

UNTRAINED_MODEL = config['artifacts']['UNTRAINED_MODEL_FILE_PATH']
TRAINED_MODEL_FILE_PATH = config['artifacts']['TRAINED_MODEL_FILE_PATH']
BLESSED_MODEL_FILE_PATH = config['artifacts']['BLESSED_MODEL_FILE_PATH']
LOGS_DIR = config['logs']['LOGS_DIR']
LOGS_FILE_PATH = config['logs']['RUNNING_LOGS_FILE_PATH']
TENSORBOARD_ROOT_LOGS_DIR = config['logs']['TENSORBOARD_ROOT_LOGS_DIR']
MODEL_EVAL_DIR = config['artifacts']['MODEL_EVAL_DIR'] 
CHECKPOINTS_DIR = config['artifacts']['CHECKPOINTS_DIR']
ARTIFACTS = config['artifacts']['ARTIFACTS_DIR']

class CloudSync:
    def __init__(self):
        self.gcs = BucketGCP(bucket_name = BUCKET_NAME)
        
    def sync_local_data_dir_to_gcs(self):
        cmd = f"gsutil -m cp -R {LOCAL_DATA_DIR} gs://{GCS_DATA_DIR}"
        os.system(cmd)

    def sync_gcs_to_local_data_dir(self):
        cmd = f"gsutil -m cp -R gs://{GCS_DATA_DIR}/dataset ./"
        os.system(cmd)

    def sync_tensorboard_logs_dir_to_gcs(self):
        cmd = f"gsutil -m cp -R {TENSORBOARD_ROOT_LOGS_DIR} gs://{GS_LOGS_DIR}"
        os.system(cmd)

    def sync_gcs_to_tensorboard_logs_dir(self):
        cmd = f"gsutil -m cp -R gs://{GS_TENSORBOARD_ROOT_LOGS_DIR} {LOGS_DIR}"
        os.system(cmd)

    def sync_model_eval_dir_to_gcs(self):
        cmd = f"gsutil -m cp -R {MODEL_EVAL_DIR} gs://{GS_ARTIFACTS}"
        os.system(cmd)

    def sync_checkpoints_dir_to_gcs(self):
        cmd = f"gsutil -m cp -R {CHECKPOINTS_DIR} gs://{GS_ARTIFACTS}"
        os.system(cmd)

    def sync_gcs_to_checkpoints_dir(self):
        cmd = f"gsutil -m cp -R gs://{GS_CHECKPOINTS_DIR} {ARTIFACTS}"
        os.system(cmd)

    def upload_untrained_full_model(self):
        self.gcs.upload_file(UNTRAINED_MODEL, GS_UNTRAINED_MODEL)

    def upload_trained_model(self):
        self.gcs.upload_file(TRAINED_MODEL_FILE_PATH, GS_TRAINED_MODEL)

    def upload_blessed_model(self):
        self.gcs.upload_file(BLESSED_MODEL_FILE_PATH, GS_BLESSED_MODEL)

    def upload_logs(self):
        self.gcs.upload_file(LOGS_FILE_PATH, GS_LOGS_FILE_PATH)


    def download_untrained_model(self):
        self.gcs.download_file(GS_UNTRAINED_MODEL, UNTRAINED_MODEL)

    def download_trained_model(self):
        self.gcs.download_file(GS_TRAINED_MODEL, TRAINED_MODEL_FILE_PATH)

    def download_blessed_model(self):
        self.gcs.download_file(GS_BLESSED_MODEL, BLESSED_MODEL_FILE_PATH)

    def download_logs(self):
        self.gcs.download_file(GS_LOGS_FILE_PATH, LOGS_FILE_PATH)
