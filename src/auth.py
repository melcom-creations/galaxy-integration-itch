import re
from urllib.parse import parse_qs, urlparse


PROVIDER = "itch.io"
PLUGIN_GUID = "2df02142-4d8a-4a4b-9b6e-c3a0bc62f93b"
CALLBACK_HOST = "127.0.0.1"
CALLBACK_PORT = 7157
CALLBACK_PATH = "/gogg2itchintegration"
_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9._~-]{16,512}$")


class TokenInputError(ValueError):
    pass


def is_plausible_token(value) -> bool:
    return isinstance(value, str) and _TOKEN_PATTERN.fullmatch(value.strip()) is not None


def parse_token_input(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TokenInputError("Enter the itch.io API token or the complete callback URL.")

    value = value.strip()
    if "://" in value:
        parsed = urlparse(value)
        try:
            port = parsed.port
        except ValueError as error:
            raise TokenInputError("The itch.io callback URL is invalid.") from error
        if (
            parsed.scheme.lower() != "http"
            or (parsed.hostname or "").lower() != CALLBACK_HOST
            or port != CALLBACK_PORT
            or parsed.path.rstrip("/") != CALLBACK_PATH
        ):
            raise TokenInputError("The itch.io callback URL is invalid.")
        values = parse_qs(parsed.fragment, keep_blank_values=True).get("access_token", [])
        if len(values) != 1:
            raise TokenInputError("The itch.io callback URL contains no usable access_token.")
        token = values[0].strip()
    elif value.startswith("access_token="):
        token = value.partition("=")[2].strip()
    else:
        token = value

    if not is_plausible_token(token):
        raise TokenInputError("The itch.io API token format is invalid.")
    return token
