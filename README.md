# 🎉 CONFGETTI 🎉

*latest version 0.1.6*

[![pipeline status](https://gl.sds.rocks/GDNI/confgetti/badges/master/pipeline.svg)](https://gl.sds.rocks/GDNI/confgetti/commits/master)
[![coverage report](https://gl.sds.rocks/GDNI/confgetti/badges/master/coverage.svg)](https://gl.sds.rocks/GDNI/confgetti/commits/master)

#### Tool for configuration and variables managment.

Fetch variables for your application easily from **Consul KV** ➡️ **config\*.json** ➡️ **environment.** via simple python method/s!

## Content

1. [Installation and Quick start](#installation-and-quick-start)
    1. [Install with pip](#install-confgetti-with-pip)
    2. [Get single variable](#get-single-variable)
    3. [Get multiple variables](#get-multiple-variables)
    4. [Override module variables](#override-current-module-variables)
2. [The Problem](#the-problem)
    1. [King of n00bs way](#1-king-of-n00bs-way)
    2. [Slightly less n00b way](#2-slightly-less-n00b-way)
3. [The Solution](#the-solution)
    1. [Logic flow](#logic-flow)
4. [Consul settings](#consul-settings)
    1. [Through environment variables](#through-environment-variables)
    2. [Upon initialization](#upon-initialization)
5. [API](#api)
    1. [Shorthand methods](#shorthand-methods)
        1. [get_variables](#confgettiget_variablespath-keys-use_envtrue-use_consultrue)
        2. [load_and_validate_config](#confgettiload_and_validate_configconfig_module_name-env_var-schemanone-keysnone-uppercasefalse)
    2. [Confgetti](#confgetticonfgetti-class)
        1. [get_variable](#confgetticonfgettiget_variablekey-pathnone-fallbacknone-convert_tonone-use_envtrue-use_consultrue)
        2. [get_variables](#confgetticonfgettiget_variablespathnone-keysnone-use_envtrue-use_consultrue)
6. [Demos](#demos)


## Installation and Quick start

### Install **Confgetti** with `pip`:

```
pip install confgetti
```

### Get single variable:

```python
# my_app/config.py
from Confgetti import get_variable

cgtti = Confgetti({'host': 'consul_instance_host'})

my_variable = cgtti.get_variable('MY_VARIABLE')
```

### Get multiple variables:

```python
# my_app/config.py
from Confgetti import get_variable

cgtti = Confgetti({'host': 'consul_instance_host'})

my_variables_dict = cgtti.get_variables(keys=[
    'MY_VARIABLE',
    'YOUR_VARIABLE',
    'OUR_VARIABLE'
])
```

### Override current module variables:


1. `ENV CONSUL_HOST=consul_instance_host`
2. variables under `MY_APP` namespace in consul

```python
# my_app/config.py
from voluptuous import Schema, Coerce
from confgetti import load_and_validate_config


my_variable = None
your_variable = None

_schema = Schema({
    "my_variable": str,
    "your_variable": Coerce(int)
})


load_and_validate_config(__name__, 'MY_APP', _schema)

```
```python
# my_app/some_logic.py
from .config import my_variable, your_variable

print(my_variable)  # should be string and not None
print(your_variable  # should be integer and not None

```


## The Problem

Modern web app development and deployment oftenly considers isolated app enviroments which are easily manageble, and quickly delpoyed with software as **VM**s or **Docker**.  
As your app gets bigger and needs more and more *settings* variables declared in you configuration modules or classes, management of those variables becomes frustrating, especially for those who manage production state of app or multiple apps and do not care of actually application code.

Imagine simple web application that uses database for data storage, cache mechanism and AWS S3 Bucket static file storage. Oh yes, and our app is Dockerized.  
To run that app successfully usually you need to pass configruation variables to methods/drivers that are communicating with those services. So at least, you'll need:

1. **Database**
    1. Database name
    2. Host
    3. Username
    4. Password
    5. Port?
2. **Cache**
    1. Host
    2. Index?
    3. Username?
    4. Password?
3. **S3 Bucket**
    1. AWS secret access key
    2. AWS access key id
    3. Bucket name

So for just **3** external services we could end with up to **12** different settings variables that are crucial for successful running of our simple web app.

How you deal a problem like a *n00b*?

#### 1. "King of n00bs" way

You could always leave those variable hardcoded to your configruation module, but prehaps, what if suddenly you need to switch to different AWS user and use different bucket? 

We even do not touch application code or logic actually but we need to:
1. push those changes to our repository (wait for Merge request, eh?)
2. build new Docker image
3. deploy new image

Whole deployment process just because  of those **3** simple variables. Not to mention that there are some sensitive data in those **12** variables, so storing them inside codebase is **NEVER** a good idea and **ALWAYS** security issue.

#### 2. "Slightly less n00b" way

Most common way of variables management, especially in Docker world, is to assign necessary variables into container environment via Docker runner and then get them from application code by checking value of some agreed and known environment key name.

If we put aside security problem of such approach (yes, environment variables could be readable by malicious user), there is still one more common and frustrating problem: A bunch of sensitive variables that need to be correctly passed each time as our Docker container is restarted or redeployed.

Each time you need to pass those **12** variables to `docker` command, and even with `docker-compose` you still need to declare those variables in `docker-compose.yml` file which returns us to previous **"King of n00bs" way**.

Do not forget, we are dealing with just one simple web app. Imagine a size of the problem on some cluster of web apps. Your DevOps(in most cases you) will hate you.


## The Solution

Here comes **Confgetti** to save a day! 🎉🎉🎉

**Confgetti** uses [Consul](https://www.consul.io) key/value storage for setting and getting your variables.
If you have running consul instance and `MY_VARIABLE` exists in its KV, you can get it simple as that:

```python
from Confgetti import get_variable

cgtti = Confgetti({'host': 'consul_instance_host'})

my_variable = cgtti.get_variable('MY_VARIABLE')
```

Maybe you still want to store some or all variables into environment?  
No problem!
**Confgetti** can get variable from your environment also.

So now we set environment variable `MY_VARIABLE` with some custom value.  
How to get variable from environment?  
With same `get_variable` method used in example above.  
No need for extra setup, custom code or monkey patching and it is beacuse of **Confgetti** efficient logic flow.

### Logic flow

**Confgetti** tries to fetch variable from two different sources in order, overriding previous source result. 
When you ask for variable with `get_variable`, lookup is made in following order:

**Consul**  
⬇️  
**environment**  
⬇️  
App  

So if you have `MY_VARIABLE` key stored in consul and in environment, **Confgetti** will return value
stored in environment (if you do not tell **Confgetti** otherwise.).  
**Confgetti** does not punish you if you do not have Consul server running, it will still return value from environment variable!

Slightly *high-level* function [load_and_validate_config](#confgettiload_and_validate_configconfig_module_name-env_var-schemanone-keysnone-uppercasefalse), that is used for fetching multiple variables at once and overriding declared module variables, will try to get variable from one extra
source, local json configuration file in following order:

**Consul**  
⬇️   
**config.json**  
⬇️  
**environment**  
⬇️  
App

With same *override* logic.


## Consul settings

**Confgetti** uses [python-consul](https://python-consul.readthedocs.io/en/latest/) package for communication with Consul's KV store.

Default connection settings are:

host: **consul**  
port: **8500**  
scheme: **http**  

Connection settings can be configured in **2** ways:

### Through environment variables

#### Available environment variables:

```
CONSUL_HOST - default: 'consul'
CONSUL_PORT - default: 8500
CONSUL_SCHEME - default: 'http'
CONSUL_TOKEN - default: None
CONSUL_DC - default: None
```

#### Example

You have running consul instance on `my_host`, port `7500`, and on secured `https`,
all you need to set following environment variables:

```
CONSUL_HOST=my_host
CONSUL_PORT=7500
CONSUL_SCHEME=https
``` 

And you do not have to pass any configuration dictionary when initializing Confgetti, because
it will read settings from environment.

```python
# my_app/config.py
from Confgetti import get_variable

cgtti = Confgetti()

my_variable = cgtti.get_variable('MY_VARIABLE')
```

> **!!!ALERT:** This is only way of configuration for `load_and_validate_config` shorthand use.

### Upon initialization

When initializing **Confgetti** instance you can pass dictionary with **Consnul** connection settings.

#### Default configuration dictionary

```python
consul_settings = {
    'host': 'consul',
    'port': 8500,
    'scheme': 'http',
    'token': None,
    'dc': None
}
```

#### Example

You have running consul instance on `my_host`, port `7500`, and on secured `https`:

```python
# my_app/config.py
from Confgetti import get_variable

cgtti = Confgetti({
    'host': 'my_host'
    'port': 7500,
    'scheme': 'https'
})

my_variable = cgtti.get_variable('MY_VARIABLE')
```

## API

### Shorthand methods

> **!!!ALERT:** If you are using shorthand functions, make sure that you have provided **Consul** connection settings via environment variables!
 
#### confgetti.get_variables(path, keys, use_env=True, use_consul=True))

This is shorthand function for `confgetti.Confgetti.get_variables`.
Used for fetching multiple variables at once from **Consul** or environment. Returns dictionary for fetched variables.

**Arguments:**  
- **path**(optional) - Namespace of variable location insike **Consul** KV storage. By default as `None` it looks to root of KV for variable.
- **keys** - list of keys under which variables are defined. This can be plain `list` of names, or `dict` where key is key name of variable and value type of value that should be returned. By default, variables are returned as **string**. Available types: `str`, `int`, `bool`, `float`, `dict`. For example:

    ```python
    my_variables_dict = cgtti.get_variables(keys=[
        'MY_VARIABLE',
        'YOUR_VARIABLE',
        'OUR_VARIABLE'
    ])
    ```

    or

    ```python
    my_variables_dict = cgtti.get_variables(keys={
        'MY_VARIABLE': str,
        'YOUR_VARIABLE': bool,
        'OUR_VARIABLE': int
    })
    ```

- **use_env**(optional) - should **Confgetti** look to environment or no?  
- **use_consul**(optional) - should **Confgetti** look to **Consul** or no?


**Example:**  
```python
from confgetti import get_variables

convert_dict = {
    "my_variable": str,
    "your_variable": int,
    "my_bool": bool,
    "my_env_variable": str
}

variables = get_variables(path='AWESOMEAPP', keys=convert_dict)
```

#### confgetti.load_and_validate_config(config_module_name, env_var, schema=None, keys=None, uppercase=False)

Used for overriding current module variables. Usually it is used with [voluptuous.Schema](http://alecthomas.github.io/voluptuous/docs/_build/html/index.html) as `schema` argument for validation, but can be used without it, or with some custom method.

**Arguments:**  
- **config_module_name** - Usually `__name__` variable from current configuration file  
- **env_var** - Prefix of variables in environment, namespace of variables location in **CONSUL** and key under which `json` configuration path is stored in environment. See example for better understanding.  
- **schema**(optional) - Pass custom method here that should return `dict` of variables which will be glued to module later. Usually used with [voluptuous.Schema](http://alecthomas.github.io/voluptuous/docs/_build/html/index.html).  
- **keys**(optional) - variable names list or dict with desired type. If you do not pass this, and you pass `voluptuous.Schema` under `schema` argument, method will return variables declared dict passed to `Schema` instance.  
- **uppercase**(optional) - By default, variables are *glued* to module in lowercase. If this is passed as `True`, variables will be *glued* in uppercase.  

**Example:**  

- *variables must be defined under `MY_APP` namespace in consul*
- *if `configuration.json` is used, enviroment variable `MY_APP` must be set with path to the file

```python
# my_app/config.py
from voluptuous import Schema, Coerce
from confgetti import load_and_validate_config


my_variable = None
your_variable = None

_schema = Schema({
    "my_variable": str,
    "your_variable": Coerce(int)
})


load_and_validate_config(__name__, 'MY_APP', _schema)

```
```python
# my_app/some_logic.py
from .config import my_variable, your_variable

print(my_variable)  # should be string and not None
print(your_variable  # should be integer and not None

```

### confgetti.Confgetti class

#### confgetti.Confgetti.get_variable(key, path=None, fallback=None, convert_to=None, use_env=True, use_consul=True)

Used for fetching single variable from **Consul** or environment. Returns single variable value

**Arguments:**  
- **key** - key under which variable is defined  
- **path**(optional) - Namespace of variable location insike **Consul** KV storage. By default as `None` it looks to root of KV for variable.  
- **fallback**(optional) - what is returned if variable is not found  
- **convert_to**(optional) - should variable be converted to certain type? If type is passed, **Confgetti** tries to convert variable to passed type. By default, variable is returend as **string**. Available types: `str`, `int`, `bool`, `float`, `dict`
- **use_env**(optional) - should **Confgetti** look to environment or no?  
- **use_consul**(optional) - should **Confgetti** look to **Consul** or no?  

**Example:**  

```python
from confgetti import Confgetti

cgtti = Confgetti()

my_variable = cgtti.get_variable('my_variable')
```

#### confgetti.Confgetti.get_variables(path=None, keys=None, use_env=True, use_consul=True)

This is internal method that is used for [get_variables](#confgettiget_variablespath-keys-use_envtrue-use_consultrue) shorthand. Arguments and logic is exactly the same.

**Example:**  

```python
from confgetti import Confgetti

cgtti = Confgetti()

my_variable = cgtti.get_variables(['my_variable', 'your_variable'])
```

## Demos

Check [demos](https://gl.sds.rocks/GDNI/confgetti/tree/feature/documentation/demos) folder for example usages as simple python scripts.
