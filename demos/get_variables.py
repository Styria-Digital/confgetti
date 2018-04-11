import os

from confgetti import get_variables


# make sure that consul host is running on yout local machine
os.environ['CONSUL_HOST'] = '127.0.0.1'
os.environ['my_bool'] = 'False'
os.environ['my_env_variable'] = 'something'

convert_dict = {
    "my_variable": str,
    "your_variable": int,
    "my_bool": bool,
    "my_env_variable": str
}


variables = get_variables(path='AWESOMEAPP', keys=convert_dict)

print(variables) 
# should be: {
# 'my_variable': 'something', 
# 'your_variable': 4, 
# 'my_bool': False, 
# 'my_env_variable': 'something'
# }
