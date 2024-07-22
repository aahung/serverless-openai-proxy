from functools import lru_cache
import json
import requests
from botocore.config import Config
from aws_lambda_powertools.utilities import parameters

from interceptors.util_encrypt import decrypt_api_key
from interceptors.util_http import (
    ForbiddenException,
    UnauthorizedException,
    get_custom_header_value,
    get_header_value,
    http_with_cors,
    set_header_value,
)

config = Config(region_name="us-east-1")
ssm_provider = parameters.SSMProvider(config=config)

ALLOWED_ORG_IDS_CUSTOM_HEADER = "x-allowlisted-organizaion-ids"
ENC_KEY_CUSTOM_HEADER = "x-api-key-encryption-key-name"
USE_ENCRYPTION_CUSTOM_HEADER = "x-use-api-key-encryption"


@lru_cache
def is_api_key_allowed(
    api_key: str, allowlisted_organization_ids: tuple[str, ...]
) -> bool:
    if not allowlisted_organization_ids:
        return True
    try:
        response = requests.get(
            "https://api.openai.com/v1/me",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        if response.status_code != 200:
            return False
        return any(
            org["id"] in allowlisted_organization_ids
            for org in response.json()["orgs"]["data"]
        )
    except Exception:
        return False


def _decrypt_key(
    api_key: str, api_key_encryption_key_name: str, *, use_api_key_encryption: bool
) -> str:
    api_key_encryption_key = ssm_provider.get(api_key_encryption_key_name, decrypt=True)
    if api_key.startswith("sk-"):
        raise UnauthorizedException(
            "Raw API key not allowed. Please reach out to your organization administrator to get access."
        )
    try:
        return decrypt_api_key(api_key_encryption_key, api_key)
    except Exception:
        raise UnauthorizedException(
            "API key is in wrong format. Please reach out to your organization administrator to get access."
        )


@http_with_cors
def lambda_handler(request, _context):
    try:
        auth_header = get_header_value(request, "authorization")
    except:  # noqa: E722
        auth_header = None
    if not auth_header:
        raise UnauthorizedException("Missing authorization header")

    allowlisted_organization_ids = tuple(
        json.loads(get_custom_header_value(request, ALLOWED_ORG_IDS_CUSTOM_HEADER))
    )
    api_key_encryption_key_name = get_custom_header_value(
        request, ENC_KEY_CUSTOM_HEADER
    )
    use_api_key_encryption = "true" == get_custom_header_value(
        request, USE_ENCRYPTION_CUSTOM_HEADER
    )
    api_key = auth_header.split(" ")[1]
    if use_api_key_encryption:
        api_key = _decrypt_key(
            api_key,
            api_key_encryption_key_name,
            use_api_key_encryption=use_api_key_encryption,
        )
        set_header_value(request, "authorization", f"Bearer {api_key}")
    if not is_api_key_allowed(api_key, allowlisted_organization_ids):
        raise ForbiddenException(
            "API key not allowed. Please reach out to your organization administrator to get access."
        )
    return request
