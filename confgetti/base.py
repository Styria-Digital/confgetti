import os
import logging
import json

from requests.exceptions import ConnectionError

from confgetti.logger import DuplicateFilter
from confgetti.remote import ConsulInterface
from confgetti.exceptions import UndefinedConnectionError, ConvertValueError


log = logging.getLogger(__name__)
log.addFilter(DuplicateFilter())


class ValueConvert(object):
    def __init__(self):
        """
        Declares boolean comparison lists under which
        strings are converted to booleans.
        """
        self.false_compare_list = ['false', 'False']
        self.true_compare_list = ['true', 'True']

    def convert_bool(self, value):
        """
        Converts string to boolean if value found in one of compare lists.

        :param value: value for conversion
        :type value: string

        :returns: converted value to new type or in original type
        :rtype: boolean/string
        """
        if value in self.false_compare_list:
            value = False
        elif value in self.true_compare_list:
            value = True
        else:
            raise ConvertValueError

        return value

    def convert_int(self, value):
        """
        Converts string to integer.

        :param value: value for conversion
        :type value: string

        :returns: converted value to new type or in original type
        :rtype: integer/string
        """
        try:
            value = int(value)
        except ValueError:
            raise ConvertValueError

        return value

    def convert_float(self, value):
        """
        Converts string to float.

        :param value: value for conversion
        :type value: string

        :returns: converted value to new type or in original type
        :rtype: float/string
        """
        try:
            value = float(value)
        except ValueError:
            raise ConvertValueError

        return value

    def convert_str(self, value):
        """
        Converts value to string.

        :param value: value for conversion
        :type value: string

        :returns: converted value to new type or in original type
        :rtype: string
        """
        return str(value)

    def convert_dict(self, value):
        """
        Converts string to dictionary.

        :param value: value for conversion
        :type value: dictionary

        :returns: converted value to new type or in original type
        :rtype: dictionary/string
        """
        try:
            value = json.loads(value)
        except json.decoder.JSONDecodeError:
            raise ConvertValueError

        return value

    def convert(self, value, convert_to=None):
        """
        Seeks for existing method based on wanted type.
        Converts value from bytes to string.
        Runs convert method if one found, if method raises error it logs
        warning.
        If method does not exists it logs warning about not supported
        conversion try.

        :param value: value for conversion
        :type value: any
        :param value: name of wanted value type
        :type value: string

        :returns: converted value to new type or in original type
        :rtype: any
        """
        if type(value) == bytes:
            value = value.decode('ascii')

        if convert_to is not None:
            if isinstance(convert_to, str):
                convert_name = convert_to
            else:
                convert_name = convert_to.__name__

            convert_method_name = 'convert_{0}'.format(convert_name)
            has_convert_method = hasattr(self, convert_method_name)

            if has_convert_method is True:
                convert_method = getattr(self, convert_method_name)
                
                try:
                    value = convert_method(value)
                except ConvertValueError:
                    log.warning('"{0}" cannot be converted to {1}!'.format(
                        value, convert_name
                    ))
            else:
                log.warning(
                    'method for "{0}" does not exist!'.format(
                        convert_name
                    )
                )

        return value


class Confgetti(object):
    """
    Declares classes for easier override if custom logic is needed.
    """
    consul_interface_class = ConsulInterface
    value_convert_class = ValueConvert

    def __init__(self, consul_config=None, prepare_consul=True):
        """
        Uses passed consul configuration to initalize consul interface,
        if configuration is passed. In other case, uses default configuration
        which is defined from environment variables.

        :param prepare_consul: shoud consul client be prepared or no
        :type prepare_consul: boolean
        :param consul_config: dictionary holding consul configuration data
        :type consul_config: dictionary/None
        """
        self.prepare_consul = prepare_consul

        if consul_config is not None:
            self.consul = self.consul_interface_class()
            self.consul.create_connection(consul_config)
        else:
            self.consul = self.consul_interface_class(self.prepare_consul)

        self.value_convert = self.value_convert_class()

    def get_variable(
            self,
            key,
            path=None,
            fallback=None,
            convert_to=None,
            use_env=True,
            use_consul=True):
        """
        Gets variable by passed key.
        It gets variable from environment and assigns it for return.
        If variable is not found in environment it tries to get variable
        from Consul service.
        If variable is not found in environment or in Consul, it returns
        fallback value.
        If variable exists, it runs conversion method based on wanted type
        provided under 'convert_to' argument.

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

        if self.prepare_consul is True and use_consul is True \
                and variable is None:
            try:
                variable = self.consul.get_raw_value(key, path)
            except (ConnectionError, UndefinedConnectionError):
                log.warning('Not connected to consul on host '
                            '"{}". Please check your consul '
                            'connection parameters!'.format(
                                self.consul.connection.http.host
                            ))

        if variable is not None:
            variable = self.value_convert.convert(variable, convert_to)

        return variable if variable is not None else fallback

    def get_variables(
            self, path=None, keys=None, use_env=True, use_consul=True):
        """
        Gets multiple variables from environment or consul, based on path.
        Supports dict and list types `keys` argument.
        In case of dict, it uses key value as conversion type,
        in case of list it just passes each key to function for getting
        variable, and everything returned is string.

        :param path: location of variable on Consul storage.
        :type path: string/None
        :param keys: set of keys whose values should be returned back
        :type keys: dict/list
        :param use_env: Should method look into environment for variable or no
        :type use_env: boolean
        :param use_consul: Should method look into consul for variable or no
        :type use_consul: boolean

        :returns: dictionary including fetched variables.
        :rtype: dict
        """
        keys = [] if keys is None else keys
        variables = {}

        if isinstance(keys, dict) is True:
            for key, value in keys.items():
                variable = self.get_variable(
                    key=key,
                    path=path,
                    convert_to=value,
                    use_env=use_env,
                    use_consul=use_consul)

                if variable is not None:
                    variables[key] = variable
        elif isinstance(keys, list) is True:
            for key in keys:
                variable = self.get_variable(
                    key=key,
                    path=path,
                    use_env=use_env,
                    use_consul=use_consul)

                if variable is not None:
                    variables[key] = variable
        else:
            raise TypeError('"keys" argument should be list or dict')

        return variables


def get_variables(path, keys, use_env=True, use_consul=True):
    """
    Shorthand function for simple Confgetti setup that returns desired
    variables in dictionary.

    :param path: location of variable on Consul storage.
    :type path: string/None
    :param keys: set of keys whose values should be returned back
    :type keys: dict/list
    :param use_env: Should method look into environment for variable or no
    :type use_env: boolean
    :param use_consul: Should method look into consul for variable or no
    :type use_consul: boolean

    :returns: dictionary including fetched variables.
    :rtype: dict
    """
    cgtti = Confgetti()

    return cgtti.get_variables(path, keys, use_env, use_consul)
