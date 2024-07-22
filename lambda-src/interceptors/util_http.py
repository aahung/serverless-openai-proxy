import json
import traceback
from http.client import responses
from typing import Any, Callable

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
                "value": "Content-Type, Authorization, OpenAI-Organization, OpenAI-Project",
            }
        ],
        "access-control-max-age": [{"key": "Access-Control-Max-Age", "value": "86400"}],
    },
    "body": "",
}


class HttpException(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


class UnauthorizedException(HttpException):
    def __init__(self, message: str):
        super().__init__(401, message)


class ForbiddenException(HttpException):
    def __init__(self, message: str):
        super().__init__(403, message)


def http_with_cors(
    lambda_handler: Callable[..., Any],
) -> Callable[..., Any]:
    def wrapper(event: dict, context: Any) -> Any:
        request = event["Records"][0]["cf"]["request"]
        if request["method"] == "OPTIONS":
            return RESPONSE_CORS
        try:
            return lambda_handler(request, context)
        except HttpException as e:
            return {
                "status": str(e.code),
                "statusDescription": responses[e.code],
                "headers": {
                    "content-type": [
                        {"key": "Content-Type", "value": "application/json"}
                    ]
                },
                "body": json.dumps(
                    {
                        "error": {
                            "message": str(e),
                        }
                    }
                ),
            }
        except Exception:
            print(traceback.format_exc())
            return {
                "status": "500",
                "statusDescription": responses[500],
                "headers": {
                    "content-type": [
                        {"key": "Content-Type", "value": "application/json"}
                    ]
                },
                "body": json.dumps(
                    {
                        "error": {
                            "message": "Unknown error",
                        }
                    }
                ),
            }

    return wrapper


def get_header_value(request, header_name) -> str:
    return request["headers"][header_name][0]["value"]


def get_custom_header_value(request, header_name) -> str:
    custom_headers = request["origin"]["custom"]["customHeaders"]
    return custom_headers[header_name][0]["value"]


def set_header_value(request, header_name, header_value) -> None:
    request["headers"][header_name][0]["value"] = header_value
