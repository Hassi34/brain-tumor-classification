import tensorflow as tf
import io
from typing import Union
from tensorflow.keras.layers import (GlobalAveragePooling2D, Dense,
                                     Activation, Dropout,BatchNormalization)
import keras
from logging import RootLogger

# config = read_yaml("configs/config.yaml")
# LOGS_FILE_PATH = config['logs']['RUNNING_LOGS_FILE_PATH']
# logger = get_logger(LOGS_FILE_PATH)

def _get_model_summary(model):
    with io.StringIO() as stream:
        model.summary(
            print_fn = lambda x: stream.write(f"{x}\n")
        )
        summary_str = stream.getvalue()
    return summary_str

def get_DenseNet121_model(input_shape : list[int], model_path: str, logger: RootLogger) -> tf.keras.models.Model:
    model = tf.keras.applications.densenet.DenseNet121(input_shape = input_shape,
                                                       weights = "imagenet",
                                                       include_top = False)
    
    logger.info(f"base model summary: {_get_model_summary(model)}")
    model.save(model_path)
    logger.info(f"DenseNet121 base model saved at {model_path}")
    return model

def prepare_full_model(base_model: tf.keras.models.Model,
                       logger: RootLogger, learning_rate: float=0.001,
                       freeze_all: bool=True, freeze_till: int= None,
                       activation: str='softmax',CLASSES: int=3,
                       loss_function: str='categorical_crossentropy',
                       mertrics: str='accuracy') -> tf.keras.models.Model:
    """Prepares the complete transfer learning model architecture

    Args:
        base_model (tf.keras.models.Model): SOTA model being used for transfer learning.
        learning_rate (float, optional): Learning rate for the model training. Defaults to 0.001.
        freeze_all (bool, optional): Freezes all the layers to make them untrainable. Defaults to True.
        freeze_till (int, optional): This value defines the extent of layers that should be trained. Defaults to None.
        activation (str, optional): Activation function at final layer. Defaults to 'softmax'.
        CLASSES (int, optional): Number of target classes. Defaults to 3.
        loss_function (str, optional): Function for calculating the loss. Defaults to 'categorical_crossentropy'.
        mertrics (str, optional): Metrics to be used for model training and evaluation. Defaults to 'accuracy'.

    Returns:
        tf.keras.models.Model: Full model architecture ready to be trained.
    """    
    
    if freeze_all:
        for layer in base_model.layers:
            layer.trainable = False 
    elif (freeze_till is not None) and (freeze_till > 0):
        for layer in base_model.layers[:freeze_till]:
            layer.trainable = False 

    ## add our layers to the base model  
    x = base_model.output  
    x = GlobalAveragePooling2D()(x)
    x = Dense(units=512)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Dropout(rate=0.3)(x)
    x = Dense(units=128)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Dropout(rate=0.2)(x)
    x = Dense(units=64)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Dense(units=32, activation='relu')(x)
    predictions = Dense(CLASSES, activation=activation)(x)
    full_model = tf.keras.models.Model(base_model.input, outputs = predictions)
        
    full_model.compile(
        optimizer = tf.keras.optimizers.Adam(learning_rate = learning_rate),
        loss = loss_function,
        metrics = [mertrics]
        )

    logger.info("Custom model is compiled and ready to be trained")

    logger.info(f"full model summary: {_get_model_summary(full_model)}")

    return full_model

def load_model(model_path: str, logger: RootLogger) -> tf.keras.models.Model:
    model = tf.keras.models.load_model(model_path)
    logger.info(f"Model is loaded from {model_path}")
    #logger.info(f"untrained full model summary: \n{_get_model_summary(model)}")
    return model

def is_blessed(valid_generator : keras.preprocessing.image.DirectoryIterator,
               blessing_threshold: Union[int, float],
               trained_model_path: str,
               production_model_path:str,
               logger: RootLogger) -> bool:
    trained_model = load_model(trained_model_path, logger= logger)
    production_model = load_model(production_model_path, logger= logger)

    trained_predictions = trained_model.evaluate(valid_generator)
    production_prediction =  production_model.evaluate(valid_generator)
    train_accuracy = round(trained_predictions[1], 3)
    production_accuracy = round(production_prediction[1], 3)
    logger.info(f"Accuracy with trained model: {train_accuracy}, Accuracy with production model: {production_accuracy}")
    if train_accuracy - production_accuracy >= blessing_threshold:
        return True
    else: 
        return False