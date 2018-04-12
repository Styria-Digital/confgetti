import os
from confgetti import Confgetti

# make sure that consul host is running on yout local machine
os.environ['CONSUL_HOST'] = '127.0.0.1'

cgtti = Confgetti()

my_variable = cgtti.get_variable('my_float_value', convert_to=float)
my_second_variable = cgtti.get_variable('my_bad_float_value', convert_to=float)

# should return values as float.
print(my_variable, type(my_variable))
# should return values as string and raise warning.
print(my_second_variable, type(my_second_variable))
