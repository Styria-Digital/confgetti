import os
from confgetti import Confgetti

# make sure that consul host is running on yout local machine
os.environ['CONSUL_HOST'] = '127.0.0.1'

cgtti = Confgetti()

my_variable = cgtti.get_variable('my_json_value', convert_to=dict)
my_second_variable = cgtti.get_variable('my_bad_json_value', convert_to=dict)

# should return values as bool.
print(my_variable, type(my_variable))

# should return string and log warning
print(my_second_variable, type(my_second_variable))
