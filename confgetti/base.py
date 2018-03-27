import os
import logging

from confgetti.remote import ConsulInterface
from confgetti.exceptions import UndefinedConnectionError
from requests.exceptions import ConnectionError

log = logging.getLogger(__name__)


class Confgetti(object):
    def __init__(self, prepare_consul=True, consul_config=None):
        """
        Uses passed consul configuration to initalize consul interface,
        if configuration is passed. In other case, uses default configuration
        which is defined from environment variables.

        :param prepare_consul: shoud consul client be prepared or no
        :type prepare_consul: boolean
        :param consul_config: dictionary holding consul configuration data
        :type consul_config: dictionary/None
        """
        if consul_config is not None:
            self.consul = ConsulInterface()
            self.consul.create_connection(consul_config)
        else:
            self.consul = ConsulInterface(prepare_consul)

    def get_variable(
            self,
            key,
            path=None,
            fallback=None,
            use_env=True,
            use_consul=True):
        """
        Gets variable by passed key.
        It gets variable from environment and assigns it for return.
        If variable is not found in environment it tries to get variable
        from Consul service.
        If variable is not found in environment or in Consul, it returns
        fallback value.

        :param key: key name of desired variable
        :type key: string
        :param path: location of variable on Consul storage.
        :type path: string/None
        :param fallback: value that is returned if variable value not found
        :type fallback: any
        :param use_env: Should method look into environment for variable or no
        :type use_env: boolean
        :param use_consul: Should method look into consul for variable or no
        :type use_consul: boolean

        :returns: variable value possibly from one source or fallback.
        :rtype: any
        """
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

        # TODO: Handle conversion to wanted type of returned value or treat as string?
        # if variable is not None:
        #     pass

        return variable if variable is not None else fallback
