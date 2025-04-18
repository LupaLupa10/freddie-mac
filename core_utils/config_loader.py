import os
import yaml
from dotenv import load_dotenv
from data.freddie_mac_data import DataConfig


def load_config_from_yaml(path: str, config_class):
    load_dotenv()
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
        for key, val in raw.items():
            if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
                env_var = val.strip("${}")
                raw[key] = os.getenv(env_var)
        return config_class(**raw)