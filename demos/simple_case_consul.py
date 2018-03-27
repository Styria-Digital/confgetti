import os
from confgetti import Confgetti

# make sure that consul host is running on yout local machine
os.environ['CONSUL_HOST'] = '127.0.0.1'

cgtti = Confgetti()

my_variable = cgtti.get_variable('my_variable')

print(my_variable)  # should return my_variable value defined on consul.
