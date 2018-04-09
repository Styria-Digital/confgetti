import os

from voluptuous import Schema

from confgetti import load_and_validate_config, value_convert


# make sure that consul host is running on yout local machine
os.environ['CONSUL_HOST'] = '127.0.0.1'

my_variable = None
your_variable = None

_schema = Schema({
    "my_variable": str,
    "your_variable": int
})


load_and_validate_config(__name__, 'AWESOMEAPP', _schema)

print(my_variable)  # should be 'something'
print(your_variable, type(your_variable))  # should be '4' int
