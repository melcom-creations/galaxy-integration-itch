from __future__ import annotations

import base64
import binascii
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from auth import PLUGIN_GUID, PROVIDER, is_plausible_token
from windows_dpapi import DpapiError, protect_current_user, unprotect_current_user


SCHEMA_VERSION = 1
WINDOWS_PROTECTION = "windows-dpapi-current-user"
LOCAL_PROTECTION = "local-user-file"
AUTH_RELATIVE_PATH = Path(
    "melcom-creations",
    "GOG Galaxy Integrations",
    "itch.io",
    "auth.json",
)


class AuthFileError(ValueError):
    pass


@dataclass(frozen=True)
class StoredAuthentication:
    token: str = field(repr=False)
    created_at: int


def auth_file_path(local_app_data: str | os.PathLike[str] | None = None) -> Path:
    if local_app_data is not None:
        root = Path(local_app_data)
    elif sys.platform == "win32":
        value = os.environ.get("LOCALAPPDATA")
        if not value:
            raise AuthFileError("LOCALAPPDATA is unavailable")
        root = Path(value)
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / AUTH_RELATIVE_PATH


def prepare_auth_file(path: Path | None = None) -> Path:
    target = path or auth_file_path()
    if target.is_file():
        return target
    _write_payload(
        {
            "schema_version": SCHEMA_VERSION,
            "provider": PROVIDER,
            "plugin_guid": PLUGIN_GUID,
            "status": "setup-required",
        },
        target,
    )
    return target


def read_auth_file(path: Path | None = None) -> StoredAuthentication | None:
    target = path or auth_file_path()
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AuthFileError("Authentication file cannot be read") from error

    if not isinstance(payload, dict):
        raise AuthFileError("Authentication file root is invalid")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise AuthFileError("Authentication file schema is invalid")
    if payload.get("provider") != PROVIDER:
        raise AuthFileError("Authentication file provider is invalid")
    if payload.get("plugin_guid") != PLUGIN_GUID:
        raise AuthFileError("Authentication file plugin GUID is invalid")
    if payload.get("status") == "setup-required":
        return None

    protection = payload.get("protection")
    try:
        if protection == WINDOWS_PROTECTION:
            protected_value = payload.get("protected_token")
            if not isinstance(protected_value, str) or not protected_value:
                raise AuthFileError("Protected itch.io token is invalid")
            protected = base64.b64decode(protected_value, validate=True)
            token = unprotect_current_user(protected).decode("utf-8")
        elif protection == LOCAL_PROTECTION and sys.platform != "win32":
            token = payload.get("token")
        else:
            raise AuthFileError("Authentication file protection is invalid")
    except (binascii.Error, UnicodeError, DpapiError, ValueError) as error:
        if isinstance(error, AuthFileError):
            raise
        raise AuthFileError("itch.io token cannot be decrypted") from error

    if not is_plausible_token(token):
        raise AuthFileError("Authentication file token is invalid")
    created_at = payload.get("created_at")
    if not isinstance(created_at, int) or isinstance(created_at, bool) or created_at < 0:
        raise AuthFileError("Authentication file timestamp is invalid")
    return StoredAuthentication(token=token.strip(), created_at=created_at)


def write_auth_file(
    token: str,
    *,
    path: Path | None = None,
    created_at: int | None = None,
) -> Path:
    if not is_plausible_token(token):
        raise AuthFileError("Cannot store an invalid itch.io token")
    token = token.strip()
    timestamp = int(time.time()) if created_at is None else created_at
    if not isinstance(timestamp, int) or isinstance(timestamp, bool) or timestamp < 0:
        raise AuthFileError("Authentication timestamp is invalid")

    target = path or auth_file_path()
    if sys.platform == "win32":
        try:
            protected = protect_current_user(token.encode("utf-8"))
        except (DpapiError, ValueError) as error:
            raise AuthFileError("itch.io token protection failed") from error
        payload = {
            "schema_version": SCHEMA_VERSION,
            "provider": PROVIDER,
            "plugin_guid": PLUGIN_GUID,
            "protection": WINDOWS_PROTECTION,
            "protected_token": base64.b64encode(protected).decode("ascii"),
            "created_at": timestamp,
        }
    else:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "provider": PROVIDER,
            "plugin_guid": PLUGIN_GUID,
            "protection": LOCAL_PROTECTION,
            "token": token,
            "created_at": timestamp,
        }
    _write_payload(payload, target)
    return target


def _write_payload(payload: dict, target: Path) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    temporary_path = None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=".auth-",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(serialized)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, target)
        if sys.platform != "win32":
            target.chmod(0o600)
    except OSError as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise AuthFileError("Authentication file could not be written") from error
