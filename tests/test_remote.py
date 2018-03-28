import os
import pytest
import responses

from unittest import TestCase, mock
from fixtures import CONSUL_DUMMY_RESPONSE, CONSUL_DUMMY_RESPONSE_LEVELED

from confgetti.remote import ConsulInterface
from confgetti.exceptions import UndefinedConnectionError


class ConsulInterfaceTestCase(TestCase):
    @mock.patch.dict(os.environ, {
        'CONSUL_HOST': 'foo'
    })
    def test__init__(self):
        ci = ConsulInterface(prepare_connection=True)

        assert ci.connection.http.host == 'foo'
        assert ci.default_consul_config.get('host') == 'foo'

    def test_create_connection_default_config_from_env(self):
        ci = ConsulInterface()
        connection = ci.create_connection()

        assert connection.http.host == 'consul'

    def test_create_connection_from_passed_config(self):
        dummy_consul_config = {
            'host': 'bar',
            'port': 8600,
            'scheme': 'http',
            'token': None,
            'dc': 'mydc'
        }
        ci = ConsulInterface()
        connection = ci.create_connection(dummy_consul_config)

        assert connection.http.host == dummy_consul_config.get('host')
        assert connection.http.port == dummy_consul_config.get('port')
        assert connection.http.scheme == dummy_consul_config.get('scheme')
        assert connection.token == dummy_consul_config.get('token')
        assert connection.dc == dummy_consul_config.get('dc')

    def test_create_connection_return_exiting(self):
        dummy_consul_config = {
            'host': 'bar',
            'port': 8600,
            'scheme': 'http',
            'token': None,
            'dc': 'mydc'
        }
        ci = ConsulInterface(prepare_connection=True)

        connection = ci.create_connection(dummy_consul_config)

        assert connection.http.host != dummy_consul_config.get('host')
        assert connection.http.port != dummy_consul_config.get('port')
        assert connection.dc != dummy_consul_config.get('dc')

    def test__check_connection__error_raises(self):
        ci = ConsulInterface()

        with pytest.raises(UndefinedConnectionError) as excinfo:
            ci._check_connection()

        assert str(excinfo.value) == 'Consul connection is not defined!'

    @responses.activate
    def test_get_raw_value(self):
        responses.add(
            responses.GET,
            'http://consul:8500/v1/kv/my_variable',
            json=[CONSUL_DUMMY_RESPONSE],
            headers={'X-Consul-Index': '924'},
            status=200
        )

        ci = ConsulInterface(prepare_connection=True)

        assert ci.get_raw_value('my_variable') == b'foo'

    @responses.activate
    def test_get_raw_value_from_path(self):
        responses.add(
            responses.GET,
            'http://consul:8500/v1/kv/my_service/my_variable',
            json=[CONSUL_DUMMY_RESPONSE_LEVELED],
            headers={'X-Consul-Index': '924'},
            status=200
        )

        ci = ConsulInterface(prepare_connection=True)

        assert ci.get_raw_value('my_variable', path='my_service') == b'foo'

    @responses.activate
    def test_get_raw_value_key_does_not_exist(self):
        responses.add(
            responses.GET,
            'http://consul:8500/v1/kv/my_variable',
            json=[],
            headers={'X-Consul-Index': '924'},
            status=404
        )

        ci = ConsulInterface(prepare_connection=True)

        assert ci.get_raw_value('my_variable') is None
