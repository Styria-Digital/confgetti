import os

from voluptuous import Schema

from confgetti import load_and_validate_config

os.environ['AWESOMEAPP'] = 'demos/dummy/config_0.json' 
# overrides json
os.environ['AWESOMEAPP_MY_VARIABLE'] = 'foo'
os.environ['AWESOMEAPP_YOUR_VARIABLE'] = 'bar'

my_variable = None
your_variable = None

_schema = Schema({
    "my_variable": str,
    "your_variable": str
})


load_and_validate_config(__name__, 'AWESOMEAPP', _schema)

print(my_variable)  # should be 'foo'
print(your_variable)  # should be 'bar'
