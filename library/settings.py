import json
import logging
import os


class JsonConfig:  # pragma: no cover
    """Allow to override settings by external configuration."""

    def __init__(self, config):
        """Initialize config with dictionary."""
        self._config = config
        self.logging = logging.getLogger("Settings")
        self.logging.propagate = False
        level = logging.INFO
        if "DEBUG" in os.environ and (
                os.environ["DEBUG"]
                or os.environ["DEBUG"].lower() in ("true", "t", "yes", "y")
        ):
            level = logging.DEBUG
        self.logging.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter("%(asctime)s [Settings] %(message)s"))
        self.logging.addHandler(handler)
        self.logging.info("Setting config.")
        self.logging.debug("Running in debug mode.")

    @classmethod
    def read(cls, envvar="CONFIG_FILE", filename="config.json"):
        """Read a JSON configuration file and create a new configuration."""
        filename = os.environ.get(envvar, filename)
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = directory + "/" + filename
        try:
            with open(filename, "r") as config_file:
                config = json.loads(config_file.read())
        except FileNotFoundError:
            config = {}

        return cls(config)

    def get(self, key, default=None):
        """Retrieve settings value for a given key."""
        value = os.environ.get(key)

        if value:
            self.logging.info("Got %s from environment." % key)
            self.logging.debug(value)
            return_val = value
        elif key in self._config.keys():
            self.logging.info("Got %s from config file." % key)
            self.logging.debug(value)
            return_val = self._config[key]
        else:
            return_val = default
        return return_val

    def get_bool(self, key, default):
        """Retrieve boolean settings value."""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return value.lower() in ("true", "t", "yes", "y")


CONFIG = JsonConfig.read()

# Config keys

API_URL = CONFIG.get('API_URL', 'https://%s.api.riotgames.com')

API_KEY = CONFIG.get("API_KEY", None)
LIMIT_SHARE = int(CONFIG.get("LIMIT_SHARE", 100)) / 100
DEBUG = CONFIG.get_bool("DEBUG", False)
FIRST_LIMIT = CONFIG.get("FIRST_LIMIT", "METHOD").upper()  # APP or METHOD for ordering
if FIRST_LIMIT not in ["APP", "METHOD"]:
    CONFIG.logging.critical(
        "Illegal vallue supplied to FIRST_LIMIT. Can only be 'APP' or 'METHOD'."
    )

# Hardcoded

ALLOWED_HEADER = [
    "X-App-Rate-Limit-Count",
    "X-App-Rate-Limit",
    "X-Method-Rate-Limit-Count",
    "X-Method-Rate-Limit",
]

ALLOWED_SERVER = [
    "americas",
    "asia",
    "ap",
    "br",
    "br1",
    "esports",
    "eu",
    "eun1",
    "europe",
    "euw1",
    "jp1",
    "kr",
    "la1",
    "la2",
    "latam",
    "na",
    "na1",
    "oc1",
    "pbe1",
    "ru",
    "sea",
    "tr1",
]
