import os

from voluptuous import Schema

from confgetti import load_and_validate_config

os.environ['AWESOMEAPP'] = 'dummy/config_0.json'

my_variable = 'cloudy'
your_variable = 0

_schema = Schema({
    "my_variable": str,
    "your_variable": int
})


load_and_validate_config(__name__, 'AWESOMEAPP', _schema)

print(my_variable)  # should be 'sunny'
print(your_variable)  # should be 2
