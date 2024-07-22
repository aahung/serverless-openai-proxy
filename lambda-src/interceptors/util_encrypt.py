from cryptography.fernet import Fernet
import base64


def decrypt_api_key(encryption_key_base64: str, encrypted_api_key_base64: str) -> str:
    f = Fernet(base64.urlsafe_b64encode(base64.b64decode(encryption_key_base64)))
    return f.decrypt(base64.b64decode(encrypted_api_key_base64)).decode("utf-8")


def encrypt_api_key(encryption_key_base64: str, api_key: str) -> str:
    f = Fernet(base64.urlsafe_b64encode(base64.b64decode(encryption_key_base64)))
    return base64.b64encode(f.encrypt(api_key.encode("utf-8"))).decode("utf-8")
