from functools import lru_cache
import os
import requests
from botocore.config import Config
from aws_lambda_powertools.utilities import parameters

RESPONSE_401 = {
    "status": "401",
    "statusDescription": "Unauthorized",
    "headers": {"content-type": [{"key": "Content-Type", "value": "text/html"}]},
    "body": "<h1>401 Unauthorized</h1><p>Sorry, you are not authorized to access this page. Please check your credentials and try again.</p>",
}
RESPONSE_403 = {
    "status": "403",
    "statusDescription": "Forbidden",
    "headers": {"content-type": [{"key": "Content-Type", "value": "text/html"}]},
    "body": "<h1>403 Forbidden</h1><p>Sorry, you are not allowed to access this page. Please contact the administrator if you think this is an error.</p>",
}
RESPONSE_CORS = {
    "status": "200",
    "statusDescription": "OK",
    "headers": {
        "access-control-allow-origin": [
            {"key": "Access-Control-Allow-Origin", "value": "*"}
        ],
        "access-control-allow-methods": [
            {
                "key": "Access-Control-Allow-Methods",
                "value": "GET, POST, PUT, DELETE, OPTIONS",
            }
        ],
        "access-control-allow-headers": [
            {
                "key": "Access-Control-Allow-Headers",
                "value": "Content-Type, Authorization",
            }
        ],
        "access-control-max-age": [{"key": "Access-Control-Max-Age", "value": "86400"}],
    },
    "body": "",
}

config = Config(region_name="us-east-1")
ssm_provider = parameters.SSMProvider(config=config)
ALLOWLISTED_ORGANIZAION_IDS = ssm_provider.get(
    f"{os.environ['AWS_LAMBDA_FUNCTION_NAME']}-allowlisted_organizaion_ids",
    transform="json",
)


@lru_cache
def is_api_key_allowed(api_key: str) -> bool:
    if not ALLOWLISTED_ORGANIZAION_IDS:
        return True
    try:
        response = requests.get(
            "https://api.openai.com/v1/me",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        if response.status_code != 200:
            return False
        return any(
            org["id"] in ALLOWLISTED_ORGANIZAION_IDS
            for org in response.json()["orgs"]["data"]
        )
    except Exception:
        return False


def lambda_handler(event, _context):
    request = event["Records"][0]["cf"]["request"]
    if request["method"] == "OPTIONS":
        print(RESPONSE_CORS)
        return RESPONSE_CORS
    try:
        auth_header = request["headers"]["authorization"][0]["value"]
    except:  # noqa: E722
        auth_header = None
    if not auth_header:
        return RESPONSE_401
    if not is_api_key_allowed(auth_header.split(" ")[1]):
        return RESPONSE_403
    return request
