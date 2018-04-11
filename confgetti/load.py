import logging
import sys
import os
import json

from voluptuous import Schema

from confgetti.base import get_variables


log = logging.getLogger(__name__)


def set_values(config_module_name, values):
    """
    Set given values to config module.

    :param config_module: python module to set values to
    :type config_module: module
    :param values: keys and values to set
    :type values: dictionary
    """
    config_module = sys.modules[config_module_name]
    for key, value in values.items():
        setattr(config_module, key, value)


def dict_keys_to_uppercase(dict_for_convert):
    """
    Converts keys of provided dict to uppercase with same value

    :param dict_for_convert: dictionary whose keys will be uppercased
    :type dict_for_convert: dictionary

    :returns: dictionary with uppercase keys
    :rtype: dictionary
    """
    converted_dict = {}

    for key, value in dict_for_convert.items():
        converted_dict[key.upper()] = value

    return converted_dict


def load_from_json(env_var):
    """
    Load config from json file.

    :param env_var: name of the env var containing path to json file.
    :type env_var: string

    :returns: config
    :rtype: dictionary
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

    :param env_prefix: prefix of env var names to get values from.
    :type env_prefix: string

    :returns: config
    :rtype: dictionary
    """
    return {key[len(env_prefix) + 1:].lower(): value
            for key, value in os.environ.items()
            if key.startswith(env_prefix) and len(key) > len(env_prefix)}


def load_from_config_server(namespace, keys):
    """
    Loads configuration from configuration server.

    :param namespace: namespace under which app configuration is located.
    :type namespace: string
    :param keys: Set of keys for variables lookup.
    :type keys: dictionary/list
    """
    return get_variables(
        path=namespace,
        keys=keys,
        use_env=False,
        use_consul=True)


def load_and_validate_config(
        config_module_name,
        env_var,
        schema=None,
        keys=None,
        uppercase=False):
    """
    Load config, validate and set to given module.

    :param config_module_name: name of the python module to set config to.
    :type config_module_name: string
    :param env_var: name of the env var containing path to config file.
    :type env_var: string
    :param schema: schema to use for config validation.
    :type schema: voluptuous.Schema
    :param uppercase: should keys be returned as uppercase or no.
    :type uppercase: boolean
    """
    if keys is None and isinstance(schema, Schema):
        keys = list(schema.schema.keys())

    try:
        config = {}

        loaded_configs = [
            load_from_config_server(env_var, keys),
            load_from_json(env_var),
            load_from_env(env_var),
        ]

        for loaded in loaded_configs:
            if uppercase is True:
                loaded = dict_keys_to_uppercase(loaded)

            config.update(loaded)

        if schema is not None:
            config = schema(config)

        set_values(config_module_name, config)
    except:
        log.error("Config error", exc_info=True)
        raise
