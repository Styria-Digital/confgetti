import os
import pytest
import responses

from unittest import TestCase, mock
from fixtures import (
    CONSUL_DUMMY_RESPONSE,
    CONSUL_DUMMY_RESPONSE_LEVELED,
    make_namespaced_responses
)

from confgetti.base import Confgetti, ValueConvert
from confgetti.exceptions import ConvertValueError


class ValueConvertTestCase(TestCase):
    def setUp(self):
        self.value_convert = ValueConvert()

    def test_convert_boolean_True_value(self):
        value = self.value_convert.convert_bool('True')

        assert value is True

    def test_convert_boolean_False_value(self):
        value = self.value_convert.convert_bool('false')

        assert value is False

    def test_convert_boolean_raises_error(self):
        with pytest.raises(ConvertValueError) as excinfo:
            self.value_convert.convert_bool('foo')

    def test_convert_integer(self):
        value = self.value_convert.convert_int('69')

        assert value == 69

    def test_convert_integer_raises_error(self):
        with pytest.raises(ConvertValueError) as excinfo:
            self.value_convert.convert_int('loo')

    def test_convert_float(self):
        value = self.value_convert.convert_float('2.99')

        assert value == 2.99

    def test_convert_float_raises_error(self):
        with pytest.raises(ConvertValueError) as excinfo:
            self.value_convert.convert_float('loo')

    def test_convert_dict(self):
        value = self.value_convert.convert_dict('{"foo":"bar", "num":3}')

        assert value == {'foo': 'bar', 'num': 3}

    def test_convert_dict_raises_error(self):
        with pytest.raises(ConvertValueError) as excinfo:
            self.value_convert.convert_dict('wannabe 3ick')

    def test_convert_value_as_bytes(self):
        value = self.value_convert.convert(b'foo')

        assert value == 'foo'
        assert isinstance(value, str) is True

    def test_convert_value_as_string(self):
        value = self.value_convert.convert('foo')

        assert value == 'foo'

    def test_convert_value_as_string_with_type(self):
        value = self.value_convert.convert('foo', convert_to=str)

        assert value == 'foo'

    def test_convert_to_is_not_None(self):
        value = self.value_convert.convert('false', convert_to=bool)

        assert value is False

    def test_convert_to_bad_value(self):
        dummy_value = 'falsey'
        value = self.value_convert.convert('falsey', convert_to=bool)

        assert value == dummy_value

    def test_convert_to_bad_desired_type(self):
        dummy_value = 'ff33aa'
        value = self.value_convert.convert('ff33aa', convert_to='hex')

        assert value == dummy_value


class ConfgettiTestCase(TestCase):
    def setUp(self):
        self.cfgtti = Confgetti(consul_config={'host': 'foobar'})

    def test__init__default_consul_config(self):
        cfgtti = Confgetti()

        assert cfgtti.consul.connection is not None

    def test__init__custom_consul_config(self):
        dummy_consul_config = {
            'host': 'bar',
            'port': 8600,
            'scheme': 'http',
            'token': None,
            'dc': 'mydc'
        }
        cfgtti = Confgetti(consul_config=dummy_consul_config)

        assert cfgtti.consul.connection.http.host == dummy_consul_config.get('host')
        assert cfgtti.consul.connection.http.port == dummy_consul_config.get('port')
        assert cfgtti.consul.connection.http.scheme == dummy_consul_config.get('scheme')
        assert cfgtti.consul.connection.token == dummy_consul_config.get('token')
        assert cfgtti.consul.connection.dc == dummy_consul_config.get('dc')

    @mock.patch.dict(os.environ, {
        'MY_DUMMY_VAR': 'foo'
    })
    def test_get_variable_from_env(self):
        variable = self.cfgtti.get_variable('MY_DUMMY_VAR')

        assert variable == 'foo'

    @responses.activate
    def test_get_variable_from_consul(self):
        responses.add(
            responses.GET,
            'http://foobar:8500/v1/kv/MY_DUMMY_VAR',
            json=[CONSUL_DUMMY_RESPONSE],
            headers={'X-Consul-Index': '924'},
            status=200
        )

        variable = self.cfgtti.get_variable('MY_DUMMY_VAR')

        assert variable == 'foo'

    @responses.activate
    def test_get_variable_do_not_use_env(self):
        responses.add(
            responses.GET,
            'http://foobar:8500/v1/kv/MY_DUMMY_VAR',
            json=[CONSUL_DUMMY_RESPONSE],
            headers={'X-Consul-Index': '924'},
            status=200
        )

        variable = self.cfgtti.get_variable('MY_DUMMY_VAR', use_env=False)

        assert variable == 'foo'

    def test_get_variable_do_not_use_consul(self):
        variable = self.cfgtti.get_variable('MY_DUMMY_VAR', use_consul=False)

        assert variable is None

    @mock.patch.dict(os.environ, {
        'MY_DUMMY_VAR': 'True'
    })
    def test_get_variable_and_convert_it(self):
        variable = self.cfgtti.get_variable(
            'MY_DUMMY_VAR', convert_to=bool)

        assert variable is True

    @responses.activate
    def test_get_variables_with_dict_keys(self):
        make_namespaced_responses()

        variables = self.cfgtti.get_variables(
            path='MYAPP',
            keys={
                'my_string_0': str,
                'my_string_1': str,
                'my_int': int,
                'my_bool': bool,
                'not_existinig': str
            }
        )

        assert variables['my_string_0'] == 'foo'
        assert variables['my_string_1'] == 'bar'
        assert variables['my_int'] == 1
        assert variables['my_bool'] is False
        assert variables.get('not_existing') is None

    @responses.activate
    def test_get_variables_with_list_keys(self):
        make_namespaced_responses()

        variables = self.cfgtti.get_variables(
            path='MYAPP',
            keys=[
                'my_string_0',
                'my_string_1',
                'my_int', 
                'my_bool',
                'not_existing'
            ]
        )

        assert variables['my_string_0'] == 'foo'
        assert variables['my_string_1'] == 'bar'
        assert variables['my_int'] == '1'
        assert variables['my_bool'] == 'false'
        assert variables.get('not_existing') is None

    @responses.activate
    def test_get_variables_with_list_keys(self):
        make_namespaced_responses()

        variables = self.cfgtti.get_variables(
            path='MYAPP',
            keys=[
                'my_string_0',
                'my_string_1',
                'my_int', 
                'my_bool',
                'not_existing'
            ]
        )

        assert variables['my_string_0'] == 'foo'
        assert variables['my_string_1'] == 'bar'
        assert variables['my_int'] == '1'
        assert variables['my_bool'] == 'false'
        assert variables.get('not_existing') is None

    @responses.activate
    def test_get_variables_with_wrong_type(self):
        with self.assertRaises(TypeError):
            variables = self.cfgtti.get_variables(
                path='MYAPP',
                keys='wrong'
            )


def test_get_variable_connection_failed(caplog):
    cfgtti = Confgetti()
    variable = cfgtti.get_variable('MY_DUMMY_VAR')

    assert 'Not connected to consul' in caplog.text
    assert variable is None
