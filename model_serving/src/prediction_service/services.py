import numpy as np
from fastapi import HTTPException, status
from src.utils.common import decode_base64_image, encode_image_into_base64
from tensorflow.keras.models import load_model
import imutils
from aipilot.tf.cv import GradCam
from PIL import Image
from typing import Union
import cv2

def prep_img(input_img_path, IMG_SIZE=224):
    if input_img_path.endswith(('.jpg','.png', '.jpeg', '.JPG', '.PNG', '.JPEG')):
        """
        Finds the extreme points on the image and crops the rectangular out of them, removes the noise and add the pseudo colors
        """
        img = cv2.imread(input_img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        # threshold the image, then perform a series of erosions +
        # dilations to remove any small regions of noise
        thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)
        # find contours in thresholded image, then grab the largest one
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)
        # find the extreme points
        extLeft = tuple(c[c[:, :, 0].argmin()][0])
        extRight = tuple(c[c[:, :, 0].argmax()][0])
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        extBot = tuple(c[c[:, :, 1].argmax()][0])
        ADD_PIXELS = 0
        new_img = img[extTop[1]-ADD_PIXELS:extBot[1]+ADD_PIXELS, extLeft[0]-ADD_PIXELS:extRight[0]+ADD_PIXELS].copy()
        new_img = cv2.cvtColor(new_img, cv2.COLOR_RGB2GRAY)
        new_img = cv2.bilateralFilter(new_img, 2, 50, 50) # remove images noise.
        new_img = cv2.applyColorMap(new_img, cv2.COLORMAP_BONE) # produce a pseudocolored image.
        new_img = cv2.resize(new_img,(IMG_SIZE,IMG_SIZE))
        cv2.imwrite(input_img_path, new_img)
        return new_img
    else:
        raise Exception("Invalid File Extension. Valid Extensions : ['.jpg','.png', '.jpeg', '.JPG', '.PNG', '.JPEG']")

def predict(base64_enc_img : str, model_path: str ,
            input_img_path: str, output_img_path: str):
    decode_base64_image(base64_enc_img, input_img_path)
    img_arr = prep_img(input_img_path=input_img_path)
    #img_arr = np.asarray(Image.open(input_img_path))
    img_arr =  np.expand_dims(img_arr, axis=0)/255.0
    model = load_model(model_path)
    prediction_proba = np.round(model.predict(img_arr), decimals = 6)
    predicted_cls = np.argmax(prediction_proba, axis=1)[0]

    gradcam = GradCam(model, "conv5_block16_concat", in_img_path= input_img_path,
                      out_img_path=output_img_path,  normalize_img=True)
    gradcam.get_gradcam()

    base64_enc_class_activation_map = encode_image_into_base64(output_img_path)
    
    prediction_proba = list(prediction_proba[0])
    prediction_proba = [round(float(i), 4) for i in prediction_proba]
    print(prediction_proba)
    if isinstance(prediction_proba, Union [list, np.ndarray]) and len(prediction_proba) == 4\
        and isinstance(prediction_proba[0], Union[float, np.float32])\
        and isinstance(prediction_proba[1], Union[float, np.float32])\
        and isinstance(prediction_proba[2], Union[float, np.float32])\
        and isinstance(prediction_proba[3], Union[float, np.float32])\
        and isinstance(base64_enc_class_activation_map, str):
        return prediction_proba, predicted_cls, base64_enc_class_activation_map
    else:
        message = "Unexpected prediction values"
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,
                            detail=message)