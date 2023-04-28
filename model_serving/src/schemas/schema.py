from pydantic import BaseModel

class Prediction(BaseModel):
    base64_enc_img : str

class ShowResults(BaseModel):
    predicted_class : int = None
    class_indices: dict = None
    prediction_probabilities : list = None
    base64_enc_class_activation_map: str = None