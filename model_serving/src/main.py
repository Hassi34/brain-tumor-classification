from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from uvicorn import run as app_run
from utils.common import read_yaml
import schemas.schema as SCHEMA
from fastapi import status
from prediction_service.services import predict

config = read_yaml('src/configs/config.yaml')

PRODUCTION_MODEL_PATH = config['model_serving']['PRODUCTION_MODEL_PATH']
APP_HOST = config['model_serving']['APP_HOST']
APP_PORT = config['model_serving']['APP_PORT']

INPUT_IMG_FILE_PATH = config['model_serving']['INPUT_IMG_FILE_PATH']
OUTPUT_IMG_FILE_PATH = config['model_serving']['OUTPUT_IMG_FILE_PATH']
CLASS_INDICES = config['model_serving']['CLASS_INDICES']

API_TITLE = config['model_serving']['API_TITLE']
API_DESCRIPTION = config['model_serving']['API_DESCRIPTION']
API_VERSION = config['model_serving']['API_VERSION']

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Authentication"])
async def index():
    return RedirectResponse(url="/docs")


@app.post('/predict', tags=["Prediction"], response_model=SCHEMA.ShowResults,
          status_code=status.HTTP_200_OK)
async def predict_route(inputParam: SCHEMA.Prediction):
    base64_enc_img = inputParam.base64_enc_img
    prediction_proba, predicted_cls, base64_enc_class_activation_map = predict(
        base64_enc_img,
        PRODUCTION_MODEL_PATH,
        INPUT_IMG_FILE_PATH,
        OUTPUT_IMG_FILE_PATH
    )

    return {"predicted_class": predicted_cls,
            "class_indices": CLASS_INDICES,
            "prediction_probabilities": prediction_proba,
            "base64_enc_class_activation_map": base64_enc_class_activation_map
            }

if __name__ == "__main__":
    app_run(app=app, host=APP_HOST, port=APP_PORT)