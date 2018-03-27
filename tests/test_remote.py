import os
import pytest
import responses

from unittest import TestCase, mock

from confgetti.remote import ConsulInterface
from confgetti.exceptions import UndefinedConnectionError


CONSUL_DUMMY_RESPONSE = {
    "LockIndex": 0,
    "Key": "my_variable",
    "Flags": 0,
    "Value": "Zm9v",
    "CreateIndex": 924,
    "ModifyIndex": 924
}

CONSUL_DUMMY_RESPONSE_LEVELED = {
    "LockIndex": 0,
    "Key": "my_service/my_variable",
    "Flags": 0,
    "Value": "Zm9v",
    "CreateIndex": 924,
    "ModifyIndex": 924
}


class ConsulInterfaceTestCase(TestCase):
    def setUp(self):
        self.cgtti = ConsulInterface()

    @mock.patch.dict(os.environ, {
        'CONSUL_HOST': 'foo'
    })
    def test__init__(self):
        cgtti = ConsulInterface(prepare_connection=True)

        assert cgtti.connection.http.host == 'foo'
        assert cgtti.default_consul_config.get('host') == 'foo'
    
    def test_create_connection_default_config_from_env(self):
        cgtti = ConsulInterface()
        connection = cgtti.create_connection()

        assert connection.http.host == 'consul'

    def test_create_connection_from_passed_config(self):
        dummy_consul_config = {
            'host': 'bar',
            'port': 8600,
            'scheme': 'http',
            'token': None,
            'dc': 'mydc'
        }
        cgtti = ConsulInterface()
        connection = cgtti.create_connection(dummy_consul_config)

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
        cgtti = ConsulInterface(prepare_connection=True)

        connection = cgtti.create_connection(dummy_consul_config)

        assert connection.http.host != dummy_consul_config.get('host')
        assert connection.http.port != dummy_consul_config.get('port')
        assert connection.dc != dummy_consul_config.get('dc')

    def test__check_connection__error_raises(self):
        cgtti = ConsulInterface()

        with pytest.raises(UndefinedConnectionError) as excinfo:
            cgtti._check_connection()

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

        cgtti = ConsulInterface(prepare_connection=True)

        assert cgtti.get_raw_value('my_variable') == b'foo'

    @responses.activate
    def test_get_raw_value_from_path(self):
        responses.add(
            responses.GET,
            'http://consul:8500/v1/kv/my_service/my_variable',
            json=[CONSUL_DUMMY_RESPONSE_LEVELED],
            headers={'X-Consul-Index': '924'},
            status=200
        )

        cgtti = ConsulInterface(prepare_connection=True)

        assert cgtti.get_raw_value('my_variable', path='my_service') == b'foo'

    @responses.activate
    def test_get_raw_value_key_does_not_exist(self):
        responses.add(
            responses.GET,
            'http://consul:8500/v1/kv/my_variable',
            json=[],
            headers={'X-Consul-Index': '924'},
            status=404
        )

        cgtti = ConsulInterface(prepare_connection=True)

        assert cgtti.get_raw_value('my_variable') is None

        
