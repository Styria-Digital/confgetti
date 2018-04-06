import unittest
import logging
import sys
import os
from unittest.mock import Mock, patch

from confgetti.override import (
    set_values, load_from_json, load_from_env, load_and_validate_config)


class SetValuesTestCase(unittest.TestCase):
    def setUp(self):
        self.module_mock = Mock()
        sys.modules["config_mock"] = self.module_mock

    def test_set_values(self):
        set_values("config_mock", {"a": True, "b": 1, "c": None, "d": "test"})

        self.assertEqual(self.module_mock.a, True)
        self.assertEqual(self.module_mock.b, 1)
        self.assertEqual(self.module_mock.c, None)
        self.assertEqual(self.module_mock.d, "test")


class LoadFromJsonTestCase(unittest.TestCase):
    def setUp(self):
        self.invalid_json = "/tmp/invalid.json"
        with open(self.invalid_json, "w") as f:
            f.write("{invalid")

        self.valid_json = "/tmp/valid.json"
        with open(self.valid_json, "w") as f:
            f.write('{"a": 1, "b": "abc"}')

    def tearDown(self):
        os.remove(self.invalid_json)
        os.remove(self.valid_json)

    def test_no_env_var(self):
        config = load_from_json("NO_VAR")
        self.assertDictEqual(config, {})

    def test_no_file(self):
        os.environ["NO_FILE"] = "/no/such/path"
        config = load_from_json("NO_FILE")
        self.assertDictEqual(config, {})

    def test_invalid_json(self):
        os.environ["INVALID_JSON"] = self.invalid_json
        with self.assertRaises(Exception):
            load_from_json("INVALID_JSON")

    def test_valid_json(self):
        os.environ["VALID_JSON"] = self.valid_json
        config = load_from_json("VALID_JSON")
        self.assertDictEqual(config, {"a": 1, "b": "abc"})


class LoadFromEnvTestCase(unittest.TestCase):
    def test_load_from_env(self):
        os.environ["PREFIX_A_B"] = "abc"
        os.environ["PREFIX_C_D"] = "123"
        os.environ["WRONG_PREFIX_E"] = "def"
        os.environ["PREFIX"] = "not"

        config = load_from_env("PREFIX")

        self.assertDictEqual(config, {"a_b": "abc", "c_d": "123"})


class LoadAndValidateConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.load_from_json_patcher = patch(
            "confgetti.override.load_from_json")
        self.load_from_json_mock = self.load_from_json_patcher.start()
        self.load_from_env_patcher = patch("confgetti.override.load_from_env")
        self.load_from_env_mock = self.load_from_env_patcher.start()
        self.set_values_patcher = patch("confgetti.override.set_values")
        self.set_values_mock = self.set_values_patcher.start()
        self.schema_mock = Mock()

    def tearDown(self):
        self.load_from_json_patcher.stop()
        self.load_from_env_patcher.stop()
        self.set_values_patcher.stop()

    def test_no_config(self):
        self.load_from_json_mock.return_value = {}
        self.load_from_env_mock.return_value = {}
        load_and_validate_config("conf", "CONF", self.schema_mock)
        self.load_from_json_mock.assert_called_once_with("CONF")
        self.load_from_env_mock.assert_called_once_with("CONF")
        self.schema_mock.assert_called_once_with({})
        self.set_values_mock.assert_called_once_with(
            "conf", self.schema_mock.return_value)

    def test_config_overrides(self):
        self.load_from_json_mock.return_value = {"a": 1, "b": "abc"}
        self.load_from_env_mock.return_value = {"a": "def", "c": 3}
        load_and_validate_config("conf", "CONF", self.schema_mock)
        self.load_from_json_mock.assert_called_once_with("CONF")
        self.load_from_env_mock.assert_called_once_with("CONF")
        self.schema_mock.assert_called_once_with(
            {"a": "def", "b": "abc", "c": 3})
        self.set_values_mock.assert_called_once_with(
            "conf", self.schema_mock.return_value)

    def test_validation_error(self):
        self.load_from_json_mock.return_value = {}
        self.load_from_env_mock.return_value = {}
        self.schema_mock.side_effect = Exception
        with self.assertRaises(Exception):
            load_and_validate_config("conf", "CONF", self.schema_mock)


def run_tests():
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_tests()
