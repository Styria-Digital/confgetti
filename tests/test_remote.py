from unittest import TestCase
import os
from unittest import TestCase, mock

from confgetti.remote import ConsulInterface


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
