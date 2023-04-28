import argparse
from src.utils.common import read_yaml
import tensorflow as tf
from aipilot.tf.cv import DataPrep
from aipilot.tf import Devices
from ml.model import load_model
from src.utils.app_logging import get_logger
from src.cloud_sync import CloudSync
from src.ml.model import is_blessed
from utils.mlflow_ops import MLFlowManager
import sys

STAGE = "Model Blessing"


def model_blessing(config_path, params_path):
    # read config files
    config = read_yaml(config_path)
    params = read_yaml(params_path)

    local_data_dir = config['local_data']['DATA_DIR']
    blessing_threshold_comparision = params['BLESSING_THRESHOLD_COMPARISION']
    model_blessing_threshold = params['MODEL_BLESSING_THRESHOLD']
    trained_model_path = config['artifacts']['TRAINED_MODEL_FILE_PATH']
    blessed_model_path = config['artifacts']['BLESSED_MODEL_FILE_PATH']

    val_split = params['VALIDATION_SPLIT_SIZE']
    batch_size = params['BATCH_SIZE']
    data_augmentation = params['DATA_AUGMENTATION']

    devices = Devices()
    devices.gpu_device
    data_ops = DataPrep(local_data_dir)

    mlflow_service = MLFlowManager()
    mlflow_model_name = config['mlflow']['MODEL_NAME']

    custom_data_augmentation = tf.keras.preprocessing.image.ImageDataGenerator(rotation_range=15,
                                                                               horizontal_flip=True,
                                                                               rescale=1./255,
                                                                               validation_split=0.2)
    train_generator, valid_generator = data_ops.data_generators(val_split=val_split,
                                                                batch_size=batch_size,
                                                                data_augmentation=data_augmentation,
                                                                augmentation_strategy=custom_data_augmentation)

    logger.info("Successfully created the data generators")

    proceed_blessing = is_blessed(valid_generator,
                                  model_blessing_threshold,
                                  trained_model_path,
                                  blessed_model_path,
                                  logger=logger)
    if blessing_threshold_comparision:
        if not proceed_blessing:
            logger.info(
                "Current model is not better than the production model, terminating the pipeline...")
            cloud_sync.upload_logs()
            sys.exit(1)

        logger.info(
            "Current model is better than the production model, proceeding with model blessing...")

        logger.info("Performing pre-blessing model validations...")
        model = load_model(trained_model_path, logger=logger)
        predictions = model.evaluate(valid_generator)

        if isinstance(predictions, list) and len(predictions) == 2 and\
                isinstance(predictions[0], float) and isinstance(predictions[1], float):
            logger.info("Model has been validated successfully")
            model.save(blessed_model_path)
            logger.info(
                f"Model has been blessed and saved at : {blessed_model_path}")
            
            latest_model_version = mlflow_service.latest_model_version(model_name=mlflow_model_name)
            mlflow_service.transition_model_version_stage(
                model_name=mlflow_model_name, model_version=latest_model_version, stage="Production")
            logger.info(
                f"Model latest version {latest_model_version} has been transitioned to MLFlow Production")
            cloud_sync.upload_blessed_model()

    else:
        logger.info(
            "Skipped model blessing as the threshold comparison has been set to 'False'")
        cloud_sync.upload_logs()
        sys.exit(0)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()
    cloud_sync = CloudSync()
    cloud_sync.download_trained_model()
    cloud_sync.download_blessed_model()
    config = read_yaml(parsed_args.config)
    LOGS_FILE_PATH = config['logs']['RUNNING_LOGS_FILE_PATH']
    logger = get_logger(LOGS_FILE_PATH)

    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        model_blessing(config_path=parsed_args.config,
                       params_path=parsed_args.params)
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
        cloud_sync.upload_logs()
    except Exception as e:
        logger.exception(e)
        cloud_sync.upload_logs()
        raise e
