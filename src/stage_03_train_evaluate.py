import argparse
from src.utils.common import read_yaml
import tensorflow as tf
from aipilot.tf.cv import DataPrep
import keras
from aipilot.tf import Devices, callbacks, Evaluator
from ml.model import load_model
import pandas as pd
from utils.app_logging import get_logger
from src.cloud_sync import CloudSync
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import mlflow 
from utils import MLFlowManager

STAGE = "Training & Evaluation"

def train_evaluate(config_path, params_path):

    config = read_yaml(config_path)
    params = read_yaml(params_path)

    local_data_dir = config['local_data']['DATA_DIR']
    tensorboard_log_dir = config['logs']['TENSORBOARD_ROOT_LOGS_DIR']
    checkpoint_file_path = config['artifacts']['CHECKPOINT_FILE_PATH']
    untrained_model_path = config['artifacts']['UNTRAINED_MODEL_FILE_PATH']
    trained_model_path = config['artifacts']['TRAINED_MODEL_FILE_PATH']
    eval_metrics_plot_file_path = config['artifacts']['MODEL_EVALUATION_PLOT']
    confusion_metrix_plot_file_path = config['artifacts']['CONFUSION_MATRIX_PLOT_FILE_PATH']

    Path(checkpoint_file_path).parent.absolute().mkdir(parents=True, exist_ok=True)
    Path(eval_metrics_plot_file_path).parent.absolute().mkdir(parents=True, exist_ok=True)

    val_split = params['VALIDATION_SPLIT_SIZE']
    batch_size = params['BATCH_SIZE']
    data_augmentation = params['DATA_AUGMENTATION']
    early_stopping_patience = params['EARLY_STOPPING_PATIENCE']
    learning_rate_patience = params['LEARNING_RATE_PATIENCE']
    epochs = params['EPOCHS']
    train_from_checkpoint = params['TRAIN_FORM_CHECKPOINT']

    devices = Devices()
    devices.gpu_device
    
    mlflow_service = MLFlowManager()
    experiment_name = config['mlflow']['EXPERIMENT_NAME']
    mlflow_model_name = config['mlflow']['MODEL_NAME']
    experiment_id = mlflow_service.get_or_create_an_experiment(experiment_name)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    run_name = config['mlflow']['RUN_ID_PREFIX'] + "-" + timestamp
    
    mlflow.tensorflow.autolog(silent=False, log_models = True,
                              registered_model_name=mlflow_model_name)
    data_ops = DataPrep(local_data_dir)

    custom_data_augmentation = tf.keras.preprocessing.image.ImageDataGenerator(rotation_range=15,
                                                                               horizontal_flip=True,
                                                                               rescale=1./255,
                                                                               validation_split= 0.2)
    train_generator, valid_generator = data_ops.data_generators( val_split=val_split,
                                                                 batch_size= batch_size,
                                                                 data_augmentation= data_augmentation,
                                                                 augmentation_strategy= custom_data_augmentation)
    steps_per_epoch = train_generator.samples // train_generator.batch_size
    validation_steps = valid_generator.samples // valid_generator.batch_size
    logger.info("Successfully created the data generators")
    (early_stopping_cb, checkpointing_cb,
    tensorboard_cb, reduce_on_plateau_cb) = callbacks(
                                                   model_ckpt_file_path = checkpoint_file_path,
                                                   tensorboard_logs_dir = tensorboard_log_dir,
                                                   es_patience = early_stopping_patience,
                                                   lr_patience = learning_rate_patience
                                                    )
    logger.info("Callbacks initialized...")
    if train_from_checkpoint:
        model = keras.models.load_model(checkpoint_file_path)
        logger.info("Started model training from the checkpoint")
    else:
        model = load_model(untrained_model_path, logger=logger)
        logger.info("Started model training from scratch")
    history = []
    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name):
        h = model.fit(
            train_generator,
            validation_data = valid_generator,
            epochs=epochs,
            steps_per_epoch=steps_per_epoch, 
            validation_steps=validation_steps,
            callbacks = [tensorboard_cb , early_stopping_cb, checkpointing_cb, reduce_on_plateau_cb]
        )
    logger.info("Model training completed successfully")
    history.append(h)
    
    history_df = pd.DataFrame()
    for h in history:
        history_df = pd.concat([history_df, pd.DataFrame.from_records(h.history)])
    fig = history_df.reset_index(drop=True).plot(figsize= (8,5)).get_figure()
    fig.savefig(eval_metrics_plot_file_path)
    plt.clf()
    logger.info(f"Evaluation Metrics plot has been saved to : {eval_metrics_plot_file_path}")
    model.save(trained_model_path)
    logger.info(f"Trained Model saved to : {trained_model_path}")
    
    eval= Evaluator(model, train_generator, valid_generator)
    matrix_plot = eval.confusion_matrix()
    matrix_plot.savefig(confusion_metrix_plot_file_path)
    logger.info(f"Confusion Matrix Plot saved to : {confusion_metrix_plot_file_path}")

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()
    cloud_sync = CloudSync()
    #cloud_sync.download_logs()
    cloud_sync.download_untrained_model()
    config = read_yaml(parsed_args.config)
    LOGS_FILE_PATH = config['logs']['RUNNING_LOGS_FILE_PATH']
    logger = get_logger(LOGS_FILE_PATH)

    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        train_evaluate(config_path=parsed_args.config, params_path=parsed_args.params)
        cloud_sync.upload_trained_model()
        cloud_sync.sync_checkpoints_dir_to_gcs()
        cloud_sync.sync_model_eval_dir_to_gcs()
        cloud_sync.sync_tensorboard_logs_dir_to_gcs()
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
        #cloud_sync.upload_logs()
    except Exception as e:
        logger.exception(e)
        cloud_sync.upload_logs()
        raise e