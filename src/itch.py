import os
import sys
import hmac

# Add the bundled modules directory to sys.path so local dependencies can be imported.
def _resolve_modules_dir():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for candidate in ('modules', 'Modules'):
        candidate_path = os.path.join(base_dir, candidate)
        if os.path.isdir(candidate_path):
            return candidate_path
    try:
        for entry in os.listdir(base_dir):
            if entry.lower() == 'modules':
                candidate_path = os.path.join(base_dir, entry)
                if os.path.isdir(candidate_path):
                    return candidate_path
    except OSError:
        pass
    return os.path.join(base_dir, 'modules')


def _normalized_path(path):
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))

modules_dir = _resolve_modules_dir()
if os.path.isdir(modules_dir):
    normalized_sys_path = {_normalized_path(p) for p in sys.path}
    resolved_modules_dir = os.path.abspath(modules_dir)
    if _normalized_path(resolved_modules_dir) not in normalized_sys_path:
        sys.path.insert(0, resolved_modules_dir)

import json
import logging
from pathlib import Path

from typing import List, Optional
from datetime import datetime
import math
import time

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform, LicenseType, OSCompatibility
from galaxy.api.types import NextStep, Authentication, Game, LicenseInfo, LocalGame, GameTime
from galaxy.api.errors import AuthenticationRequired, AccessDenied, BackendError, InvalidCredentials

from localClientDbReader import localClientDbReader
from http_client import HTTPClient
from auth_server import LocalAuthServer
from auth_storage import (
    AuthFileError,
    auth_file_path,
    prepare_auth_file,
    read_auth_file,
    write_auth_file,
)

with open(Path(__file__).parent / 'manifest.json', 'r') as f:
    __version__ = json.load(f)['version']

LEGACY_CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'
KEYS_URL = 'https://api.itch.io/profile/owned-keys?page=%s'
HOMEPAGE = 'https://www.itch.io'


class ItchIntegration(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(
            Platform.ItchIo,
            __version__,
            reader,
            writer,
            token
        )
        self.http_client = HTTPClient(self.store_credentials)
        self.auth_file = auth_file_path()
        self.auth_server = LocalAuthServer()
        self.session_cookie = None
        self.myLocalClientDbReader = localClientDbReader()

        self.myLocalClientDbReader.set_plugin_callbacks(
            self.persistent_cache,
            self.update_game_time,
            self.push_cache
        )

        self.time_last_update = datetime.now()
        self.my_handshook = False

    async def shutdown(self):
        await self.auth_server.stop()
        await self.http_client.close()

    def _load_legacy_credentials_file(self):
        if not LEGACY_CREDENTIALS_FILE.exists():
            return None

        try:
            # UTF-8-SIG ignores a Windows BOM at the start of the file.
            with open(LEGACY_CREDENTIALS_FILE, 'r', encoding='utf-8-sig') as f:
                credentials = json.load(f)
            if isinstance(credentials, dict):
                return credentials
            logging.warning("Legacy credentials.json does not contain a JSON object")
        except Exception as e:
            logging.warning("Could not read legacy credentials.json: %s", e)
        return None

    def _extract_access_token(self, credentials):
        if not isinstance(credentials, dict):
            return None

        token = credentials.get("access_token")
        if not isinstance(token, str):
            return None

        token = token.strip()
        return token or None

    async def _setup_next_step(self):
        try:
            prepare_auth_file(self.auth_file)
        except AuthFileError as error:
            logging.warning("itch.io authentication file could not be prepared: %s", error)
            raise BackendError("itch.io authentication file could not be prepared") from error

        await self.auth_server.stop()
        try:
            await self.auth_server.start()
        except OSError as error:
            logging.warning("itch.io local setup server could not be started: %s", error)
            raise BackendError("itch.io setup could not be started") from error

        logging.info("itch.io setup opened; authentication file: %s", self.auth_file)
        return NextStep(
            "web_session",
            {
                "window_title": "itch.io Plugin Setup",
                "window_width": 760,
                "window_height": 900,
                "start_uri": self.auth_server.base_url,
                "end_uri_regex": self.auth_server.end_uri_regex,
            },
        )

    async def _validate_access_token(self, access_token):
        self.http_client.update_cookies({"access_token": access_token})
        user = await self.get_user_data()
        if not isinstance(user, dict):
            raise InvalidCredentials("itch.io returned no user profile")
        user_id = user.get("id")
        username = user.get("username")
        if user_id is None or not isinstance(username, str) or not username.strip():
            raise InvalidCredentials("itch.io returned an incomplete user profile")
        return Authentication(str(user_id), username.strip())

    def _store_external_token(self, access_token):
        try:
            path = write_auth_file(access_token, path=self.auth_file)
            stored = read_auth_file(path)
        except AuthFileError as error:
            logging.warning("itch.io authentication could not be stored: %s", error)
            raise BackendError("itch.io authentication could not be stored") from error
        if stored is None or not hmac.compare_digest(stored.token, access_token):
            raise BackendError("itch.io authentication verification failed")
        self.store_credentials({})
        logging.info("Saved protected itch.io authentication to %s", path)

    async def authenticate(self, stored_credentials=None):
        logging.debug("authenticate")

        try:
            stored_authentication = read_auth_file(self.auth_file)
        except AuthFileError as error:
            logging.warning("itch.io authentication file is unavailable: %s", error)
            return await self._setup_next_step()

        if stored_authentication is not None:
            try:
                authentication = await self._validate_access_token(stored_authentication.token)
                self.store_credentials({})
                return authentication
            except (AccessDenied, AuthenticationRequired, InvalidCredentials):
                return await self._setup_next_step()

        legacy_credentials = self._load_legacy_credentials_file()
        access_token = self._extract_access_token(legacy_credentials)
        token_from_legacy_file = access_token is not None
        if not access_token:
            access_token = self._extract_access_token(stored_credentials)

        if not access_token:
            return await self._setup_next_step()

        try:
            authentication = await self._validate_access_token(access_token)
        except (AccessDenied, AuthenticationRequired, InvalidCredentials):
            return await self._setup_next_step()

        self._store_external_token(access_token)
        if token_from_legacy_file:
            try:
                LEGACY_CREDENTIALS_FILE.unlink()
                logging.info("Removed migrated legacy itch.io credentials.json")
            except OSError as error:
                logging.warning("Migrated legacy credentials.json could not be removed: %s", error)
        return authentication

    async def pass_login_credentials(self, step, credentials, cookies):
        access_token = self.auth_server.captured_token
        if not access_token:
            await self.auth_server.stop()
            raise InvalidCredentials("No itch.io API token was submitted")
        try:
            authentication = await self._validate_access_token(access_token)
            self._store_external_token(access_token)
            return authentication
        finally:
            await self.auth_server.stop()

    def handshake_complete(self):
        logging.info("Handshake complete")
        self.my_handshook = True

    async def get_owned_games(self):
        whitelist = await load_whitelist_from_file()
        page = 1
        games = []
        while True:
            try:
                resp = await self.http_client.get(f"https://api.itch.io/profile/owned-keys?classification=game&page={page}")
            except AuthenticationRequired:
                self.lost_authentication()
                raise
            if len(resp.get("owned_keys")) == 0:
                break
            self.parse_json_into_games(resp.get("owned_keys"), games, whitelist)
            page += 1

        # The itch.io "owned-keys" endpoint only lists games for which a
        # download key was claimed. Games installed via the itch app without
        # ever claiming a key (free downloads, jam entries, etc.) never show
        # up there, which meant they were completely missing from Galaxy even
        # though they are installed. Add those from the local itch client
        # database so Galaxy learns about them with a proper title.
        known_ids = {g.game_id for g in games}
        try:
            local_games = await self.myLocalClientDbReader.get_games()
        except Exception as e:
            logging.warning(f"Could not read local itch games: {e}")
            local_games = []

        for local_game in local_games:
            if local_game.game_id in known_ids:
                continue
            if whitelist and local_game.game_title not in whitelist:
                continue
            self.persistent_cache.setdefault(local_game.game_id, {"title": local_game.game_title, "traits": []})
            games.append(local_game)
            known_ids.add(local_game.game_id)

        return games

    async def get_user_data(self):
        resp = await self.http_client.get(f"https://api.itch.io/profile?")
        self.authenticated = True
        return resp.get("user")

    def parse_json_into_games(self, resp, games, whitelist):
        for key in resp:
            game = key.get("game")
            if not game.get("classification") == "game":
                continue
            game_name = game.get("title")
            game_num = str(game.get("id"))
            logging.debug('Parsed %s, %s', game_name, game_num)
            self.persistent_cache[game_num] = game
            this_game = Game(
                game_id=game_num,
                game_title=game_name,
                license_info=LicenseInfo(LicenseType.SinglePurchase),
                dlcs=[])
            if (len(whitelist) > 0):
                if (game_name in whitelist):
                    games.append(this_game)
            else:
                games.append(this_game)

    async def get_os_compatibility(self, game_id, context):
        try:
            cached_game = self.persistent_cache[str(game_id)]
            if isinstance(cached_game, str):
                cached_game = json.loads(cached_game)
            if not isinstance(cached_game, dict):
                return None
            compat = cached_game.get("traits", [])
            os_compat = (
                (OSCompatibility.Windows if "p_windows" in compat else OSCompatibility(0)) |
                (OSCompatibility.MacOS if "p_osx" in compat else OSCompatibility(0)) |
                (OSCompatibility.Linux if "p_linux" in compat else OSCompatibility(0))
            )
            logging.debug("Compat value: %s", os_compat)
            if not os_compat == 0:
                return os_compat
        except (KeyError, TypeError, json.JSONDecodeError):
            logging.error("Key not found in cache: %s", game_id)

    def tick(self) -> None:
        time_current = datetime.now()
        time_delta = (time_current - self.time_last_update)
        time_delta_seconds = time_delta.total_seconds()
        my_rounded_delta = math.floor(time_delta_seconds / 60)

        if my_rounded_delta > 0:
            self.create_task(self.myLocalClientDbReader.check_for_new_games(), "checkForNewGames")
            self.time_last_update = datetime.now()

        if (self.my_handshook):
            my_mod_delta = math.floor(time_delta_seconds / 7)
            my_counter = 0
            while my_mod_delta > 0 and my_counter < 101 and not self.myLocalClientDbReader.my_queue_update_local_game_status.empty():
                my_game_update_sending = self.myLocalClientDbReader.my_queue_update_local_game_status.get()
                logging.error(my_game_update_sending)
                self.update_local_game_status(my_game_update_sending)
                my_counter = my_counter + 1

    async def get_local_games(self) -> List[LocalGame]:
        logging.info("galaxy update local installed")
        return await self.myLocalClientDbReader.get_local_games()

    async def launch_game(self, game_id: str) -> None:
        logging.info("calling local launcher")
        await self.myLocalClientDbReader.launch_game(game_id)

    # Read the cached playtime and last-played timestamp from the local cache.
    async def get_game_time(self, game_id: str, context: None) -> GameTime:
        time_played_key = f'time{game_id}'
        last_played_key = f'last{game_id}'
        
        time_played = None
        last_played_time = None
        
        if time_played_key in self.persistent_cache:
            time_played = int(self.persistent_cache[time_played_key])
            
        if last_played_key in self.persistent_cache:
            last_played_time = int(self.persistent_cache[last_played_key])
            
        return GameTime(
            game_id=game_id,
            time_played=time_played,
            last_played_time=last_played_time,
        )


def main():
    create_and_run_plugin(ItchIntegration, sys.argv)


def log(msg):
    log_file = open(os.path.join(os.path.dirname(__file__), "log2.txt"), "a")
    log_file.write(str(msg) + "\n")
    log_file.close()

async def load_whitelist_from_file():
    ret = []
    if (os.path.isfile(Path(__file__).parent / 'whitelist.txt')):
        with open(Path(__file__).parent / 'whitelist.txt', 'r') as f:
            lines = f.readlines()
            for l in lines:
                ret.append(l.strip())
    return ret

if __name__ == "__main__":
    main()
