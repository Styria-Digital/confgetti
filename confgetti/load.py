import logging
import sys
import os
import json

log = logging.getLogger(__name__)


def set_values(config_module_name, values):
    """
    Set given values to config module.

    :param config_module: module, python module to set values to
    :param values: dict, keys and values to set
    """
    config_module = sys.modules[config_module_name]
    for key, value in values.items():
        setattr(config_module, key, value)


def load_from_json(env_var):
    """
    Load config from json file.

    :param env_var: str, name of the env var containing path to json file.
    :returns dict: config
    """
    path_to_json = os.environ.get(env_var)
    if path_to_json is None:
        log.warning("Config path set to None, unable to load "
                    "configuration: {}".format(env_var))
        return {}

    if not os.path.isfile(path_to_json):
        log.warning("Config file does not exist, unable to load "
                    "configuration: {}".format(path_to_json))
        return {}

    with open(path_to_json, "r") as f:
        return json.load(f)


def load_from_env(env_prefix):
    """
    Load config from env variables.

    :param env_prefix: str, prefix of env var names to get values from.
    :returns dict: config
    """
    return {key[len(env_prefix) + 1:].lower(): value
            for key, value in os.environ.items()
            if key.startswith(env_prefix) and len(key) > len(env_prefix)}


def load_and_validate_config(config_module_name, env_var, schema):
    """
    Load config, validate and set to given module.

    :param config_module_name: str, name of the python module to set config to.
    :param env_var: str, name of the env var containing path to config file.
    :param schema: voluptuous.Schema, schema to use for config validation.
    """
    try:
        config = {}
        config.update(load_from_json(env_var))
        config.update(load_from_env(env_var))
        config = schema(config)
        set_values(config_module_name, config)
    except:
        log.error("Config error", exc_info=True)
        raise
