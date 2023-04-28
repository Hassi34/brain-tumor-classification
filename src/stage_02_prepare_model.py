import argparse
from src.utils.common import read_yaml
from src.ml.model import get_DenseNet121_model , prepare_full_model
from src.cloud_sync import CloudSync
from utils.app_logging import get_logger

STAGE = "Prepare Model"

def prepare_model(config_path, params_path):
    config = read_yaml(config_path)
    params = read_yaml(params_path)
    
    base_model_path = config['artifacts']['BASE_MODEL_FILE_PATH']
    untrained_model_path = config['artifacts']['UNTRAINED_MODEL_FILE_PATH']
    inpute_shape = params['IMAGE_SIZE']
    classes = params['CLASSES']
    learning_rate = params['LEARNING_RATE']
    freeze_all = params['FREEZE_ALL']
    freeze_till = params['FREEZE_TILL']
    loss_function = params['LOSS_FUNCTION']
    metrics = params['METRICS']

    base_model = get_DenseNet121_model(input_shape = inpute_shape,
                                       model_path = base_model_path,
                                       logger= logger)
    logger.info("Downloaded the base model")
    logger.info("Preparing the complete model...")
    full_model = prepare_full_model(
        base_model = base_model,
        logger= logger,
        learning_rate= learning_rate,
        freeze_all= freeze_all,
        freeze_till= freeze_till,
        CLASSES = classes,
        loss_function= loss_function,
        mertrics= metrics)

    full_model.save(untrained_model_path)
    logger.info(f'Full untrained model is saved at {untrained_model_path}')

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()
    cloud_sync = CloudSync()
    #cloud_sync.download_logs()
    config = read_yaml(parsed_args.config)
    LOGS_FILE_PATH = config['logs']['RUNNING_LOGS_FILE_PATH']
    logger = get_logger(LOGS_FILE_PATH)

    try:
        logger.info("\n********************")
        logger.info(f">>>>> stage {STAGE} started <<<<<")
        prepare_model(config_path=parsed_args.config, params_path=parsed_args.params)
        cloud_sync.upload_untrained_full_model()
        logger.info(f">>>>> stage {STAGE} completed!<<<<<\n")
    except Exception as e:
        cloud_sync.upload_logs()
        logger.exception(e)
        raise e