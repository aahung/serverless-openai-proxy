import os

from pydantic import BaseModel

from interceptors.util_encrypt import encrypt_api_key
from interceptors.util_ssm import ssm_provider


class Event(BaseModel):
    api_key: str


class Response(BaseModel):
    encrypted_api_key: str


def lambda_handler(event, _context):
    api_key = Event(**event).api_key
    api_key_encryption_key_name = os.environ["API_KEY_ENCRYPTION_KEY_NAME"]
    api_key_encryption_key = ssm_provider.get(api_key_encryption_key_name, decrypt=True)
    return Response(
        encrypted_api_key=encrypt_api_key(api_key_encryption_key, api_key)
    ).model_dump()
