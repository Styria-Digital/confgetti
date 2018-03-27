import os
import consul

CONSUL_HOST = os.environ.get('CONSUL_HOST', 'consul')
CONSUL_PORT = os.environ.get('CONSUL_PORT', 8500)
CONSUL_SCHEME = os.environ.get('CONSUL_SCHEME', 'http')
CONSUL_TOKEN = os.environ.get('CONSUL_TOKEN')
CONSUL_DC = os.environ.get('CONSUL_DC')

# REMOVE
CONSUL_HOST = '127.0.0.1'


class ConsulInterface(object):
    def __init__(self, prepare_connection=False):
        self.connection = None

        if prepare_connection is True:
            self.connection = self.create_connection()

    def create_connection(
            self, host=CONSUL_HOST, port=CONSUL_PORT, scheme=CONSUL_SCHEME,
            token=CONSUL_TOKEN, dc=CONSUL_DC):

        consul_connection = consul.Consul(
            host=host,
            port=port,
            scheme=scheme,
            token=token,
            dc=dc
        )

        return consul_connection

    def get_value_for_key(self, key, path=None):
        key_location = key

        if path is not None:
            key_location = '{0}/{1}'.format(
                path, key
            )

        if self.connection is not None:
            index, data = self.connection.kv.get(key_location)

            return data.get('Value')
        else:
            raise ConnectionError

try:
    value = ConsulInterface(False).get_value_for_key('AWS_SECRET_ID', path='Sanitag')
    print(value)
except ConnectionError:
    print('Connection not defined')

