import os
import pytest
import responses

from unittest import TestCase, mock
from fixtures import CONSUL_DUMMY_RESPONSE, CONSUL_DUMMY_RESPONSE_LEVELED

from confgetti.base import Confgetti


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

        assert variable == b'foo'

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

        assert variable == b'foo'

    def test_get_variable_do_not_use_consul(self):
        variable = self.cfgtti.get_variable('MY_DUMMY_VAR', use_consul=False)

        assert variable is None


def test_get_variable_connection_failed(caplog):
    cfgtti = Confgetti()
    variable = cfgtti.get_variable('MY_DUMMY_VAR')

    assert 'Not connected to consul' in caplog.text
    assert variable is None
