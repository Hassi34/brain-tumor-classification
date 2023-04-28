import yaml
import base64

def read_yaml(path_to_yaml: str) -> dict:
    with open(path_to_yaml) as yaml_file:
        content = yaml.safe_load(yaml_file)
    return content

def decode_base64_image(img_string, file_name):
    img_data = base64.b64decode(img_string)
    with open("./"+file_name, 'wb') as f:
        f.write(img_data)
        f.close()

def encode_image_into_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")