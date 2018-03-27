import os
import consul

from requests.exceptions import ConnectionError
from confgetti.exceptions import UndefinedConnectionError


class ConsulInterface(object):
    def __init__(self, prepare_connection=False):
        self.connection = None
        self.default_consul_config = {
            'host': os.environ.get('CONSUL_HOST', 'consul'),
            'port': os.environ.get('CONSUL_PORT', 8500),
            'scheme': os.environ.get('CONSUL_SCHEME', 'http'),
            'token': os.environ.get('CONSUL_TOKEN'),
            'dc': os.environ.get('CONSUL_DC')
        }

        if prepare_connection is True:
            self.create_connection()

    def create_connection(self, config=None):
        config = self.default_consul_config if config is None else config

        if self.connection is None:
            self.connection = consul.Consul(**config)

        return self.connection

    def _check_connection(self):
        if self.connection is None:
            raise UndefinedConnectionError('Consul connection is not defined!')

    def get_raw_value(self, key, path=None):
        self._check_connection()

        value = None
        key_location = key

        if path is not None:
            key_location = '{0}/{1}'.format(
                path, key
            )

        index, data = self.connection.kv.get(key_location)

        if data is not None:
            value = data.get('Value')

        return value
