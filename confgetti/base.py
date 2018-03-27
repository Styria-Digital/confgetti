import os
import logging

from confgetti.remote import ConsulInterface
from confgetti.exceptions import UndefinedConnectionError
from requests.exceptions import ConnectionError

log = logging.getLogger(__name__)


class Confgetti(object):
    def __init__(self, prepare_consul=True, consul_config=None):
        if consul_config is not None:
            self.consul = ConsulInterface()
            self.consul.create_connection(consul_config)
        else:
            self.consul = ConsulInterface(prepare_consul)

    def get_variable(self, key, fallback=None, path=None,
                     use_env=True, use_consul=True):
        variable = None

        if use_env is True:
            variable = os.environ.get(key)

        if use_consul is True and variable is None:
            try:
                variable = self.consul.get_raw_value(key, path)
            except (ConnectionError, UndefinedConnectionError):
                log.warning('Not connected to consul on host '
                            '"{}". Please check your consul '
                            'connection parameters!'.format(
                                self.consul.connection.http.host
                            ))

        # TODO: Handle conversion to wanted type of returned value?
        # if variable is not None:
        #     pass

        return variable if variable is not None else fallback
