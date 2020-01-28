import os
from confgetti import Confgetti

# make sure that consul host is running on yout local machine
os.environ['CONSUL_HOST'] = '127.0.0.1'

cgtti = Confgetti()

my_variable = cgtti.get_variable('my_bool_value', convert_to=bool)
my_second_variable = cgtti.get_variable('my_bool_value2', convert_to=bool)
my_third_variable = cgtti.get_variable('my_bad_bool_value', convert_to=bool)

# should return values as bool.
print(my_variable, type(my_variable))
print(my_second_variable, type(my_second_variable))

# should return string and log warning
print(my_third_variable, type(my_third_variable))
