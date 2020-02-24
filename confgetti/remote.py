import os
import consul

from requests.exceptions import ConnectionError
from confgetti.exceptions import UndefinedConnectionError


class ConsulInterface(object):
    def __init__(self, prepare_connection=False):
        """
        Sets empty connection upon initialization.
        Constructs default consul configuration, that will be used in
        connection to running consul, from environment variables.
        If class object is initialized with 'prepare_connection' as True
        it runs method that connects to consul instance and attaches it to
        initialized object.

        :param prepare_connection: Initialization creates connection or not
        :type prepare_connection: boolean
        """
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
        """
        Creates connection to Consul service.
        Uses default consul configuration constructed from environment
        variables if alternate configuration is not passed to method.

        :param config: Initialization creates connection or not
        :type config: dictionary/None

        :returns: instance of consul client
        :rtype: consul.std.Consul object
        """
        config = self.default_consul_config if config is None else config

        if self.connection is None:
            self.connection = consul.Consul(**config)

        return self.connection

    def _check_connection(self):
        """
        In case when connection object is not defined on class instance,
        it raises error of undefined connection.
        """
        if self.connection is None:
            raise UndefinedConnectionError('Consul connection is not defined!')

    def get_raw_value(self, key, path=None):
        """
        Gets value from Consul's key value storage.
        Firstly, calls method for checking connection.
        Constructs key path if `path` is provided.
        Uses current connection to get value by key path.
        If storage returns data dict, it gets value from it.

        :param key: key for desired value
        :type key: string
        :param path: path where key is stored on Consul service
        :type path: string/None

        :returns: fetched value from Consul service.
        :rtype: bytes/None
        """
        self._check_connection()

        value = None
        key_path = key

        if path is not None:
            key_path = '{0}/{1}'.format(
                path, key
            )

        index, data = self.connection.kv.get(key_path)

        if data is not None:
            value = data.get('Value')

        return value
