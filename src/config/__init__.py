from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

load_dotenv()
key=os.environ['JSON_DCRYPT_KEY']
CREDENTIALS_PATH = os.path.join("src", "config", "credentials.json")
CRED_TXT = os.path.join("src", "config", "cred.txt")

fernet = Fernet(key)

with open(CRED_TXT, 'rb') as f:
    encrypted = f.read()
decrypted = fernet.decrypt(encrypted)

with open(CREDENTIALS_PATH, 'wb') as json_file:
    json_file.write(decrypted)

try:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH 
except Exception as e:
    raise e