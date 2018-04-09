import os
from confgetti import Confgetti

# make sure that consul host is running on yout local machine
os.environ['CONSUL_HOST'] = '127.0.0.1'

cgtti = Confgetti()

my_variable = cgtti.get_variable('my_integer_value', convert_to=int)
my_second_variable = cgtti.get_variable('my_bad_integer_value', convert_to=int)

# should return values as integer.
print(my_variable, type(my_variable))
# should return values as string and raise warning.
print(my_second_variable, type(my_second_variable))
