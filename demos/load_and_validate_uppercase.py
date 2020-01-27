import os

from voluptuous import Schema, Coerce

from confgetti import load_and_validate_config

os.environ['AWESOMEAPP'] = 'demos/dummy/config_0.json'
# overrides json
os.environ['AWESOMEAPP_MY_VARIABLE'] = 'foo'
os.environ['AWESOMEAPP_YOUR_VARIABLE'] = 'bar'

MY_VARIABLE = None
YOUR_VARIABLE = None

_schema = Schema({
    "MY_VARIABLE": str,
    "YOUR_VARIABLE": Coerce(str)
})


load_and_validate_config(__name__, 'AWESOMEAPP', _schema, uppercase=True)

print(MY_VARIABLE)  # should be 'foo'
print(YOUR_VARIABLE)  # should be 'bar'
