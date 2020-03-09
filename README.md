<img src="https://raw.githubusercontent.com/Styria-Digital/confgetti/master/docs/images/confgetti_logo_small.png" width="200">

[![PyPI version](https://badge.fury.io/py/confgetti.svg)](https://badge.fury.io/py/confgetti)

![](https://github.com/Styria-Digital/confgetti/workflows/Tests/badge.svg)

#### Tool for configuration and variables management.

Fetch variables for your application easily from **Consul KV** ➡️ **config\*.json** ➡️ **environment.** via simple python method/s!

## Content

1. [Installation and QuickStart](#installation-and-quickstart)
    1. [Install with pip](#install-confgetti-with-pip)
    2. [Get a single variable](#get-a-single-variable)
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
    2. [Confgetti](#confgetticonfgetticonsul_confignone-prepare_consultrue)
        1. [get_variable](#confgetticonfgettiget_variablekey-pathnone-fallbacknone-convert_tonone-use_envtrue-use_consultrue)
        2. [get_variables](#confgetticonfgettiget_variablespathnone-keysnone-use_envtrue-use_consultrue)
6. [Demos](#demos)
7. [Developer Notes](#developer-notes)
    1. [Releasing new version](#releasing-new-version)


## [Installation and QuickStart](#installation-and-quickstart)

### [Install **Confgetti** with `pip`:](#install-confgetti-with-pip)

```
pip install confgetti
```

### [Get a single variable:](#get-a-single-variable)

```python
# my_app/config.py
from Confgetti import get_variable

cgtti = Confgetti({'host': 'consul_instance_host'})

my_variable = cgtti.get_variable('MY_VARIABLE')
```

### [Get multiple variables:](#get-multiple-variables)

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

### [Override module variables:](#override-current-module-variables)


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

print(my_variable)  # should be a string and not None
print(your_variable  # should be an integer and not None

```


## [The Problem](#the-problem)

Modern web app development and deployment often consider isolated app environments that are easily manageble and quickly deployed with software as **VM**s or **Docker**.  
As your app gets bigger and needs more and more *settings* variables declared in your configuration modules or classes, management of those variables becomes frustrating, especially for those who manage the production state of the app or multiple apps and do not care about actual application code.

Imagine a simple web application that uses a database for data storage, cache mechanism, and AWS S3 Bucket static file storage. Oh yes, and our app is Dockerized.  
To run that app successfully usually you need to pass configuration variables to methods/drivers that are communicating with those services. So at least, you'll need:

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

So for just **3** external services, we could end with up to **12** different settings variables that are crucial for the successful running of our simple web app.

How do you deal with a problem like an *n00b*?

#### [1. King of n00bs way](#1-king-of-n00bs-way)

You could always leave those variable hardcoded to your configuration module, but perhaps, what if suddenly you need to switch to different AWS user and use the different bucket? 

We even do not touch application code or logic actually but we need to:
1. push those changes to our repository (wait for a Merge request, eh?)
2. build a new Docker image
3. deploy a new image

Whole deployment process just because  of those **3** simple variables. Not to mention that there are some sensitive data in those **12** variables, so storing them inside codebase is **NEVER** a good idea and **ALWAYS** security issue.

#### [2. Slightly less n00b way](#2-slightly-less-n00b-way)

The most common way of variables management, especially in the Docker world, is to assign necessary variables into the container environment via Docker runner and then get them from application code by checking the value of some agreed and known environment key name.

If we put aside the security problem of such an approach (yes, environment variables could be readable by a malicious user), there is still one more common and frustrating problem: A bunch of sensitive variables that need to be correctly passed each time as our Docker container is restarted or redeployed.

Each time you need to pass those **12** variables to `docker` command, and even with `docker-compose` you still need to declare those variables in the `docker-compose.yml` file which returns us to previous **"King of n00bs" way**.

Do not forget, we are dealing with just one simple web app. Imagine the size of the problem on some cluster of web apps. Your DevOps(in most cases you) will hate you.


## [The Solution](#the-solution)

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
**Confgetti** can get a variable from your environment also.

So now we set environment variable `MY_VARIABLE` with some custom value.  
How to get a variable from the environment?  
With the same `get_variable` method used in the example above.  
No need for extra setup, custom code or monkey patching and it is because of **Confgetti** efficient logic flow.

### [Logic flow](#logic-flow)

**Confgetti** tries to fetch a variable from two different sources in order, overriding the previous source result. 
When you ask for a variable with `get_variable`, the lookup is made in the following order:

**Consul**  
⬇️  
**environment**  
⬇️  
App  

So if you have `MY_VARIABLE` key stored in consul and in the environment, **Confgetti** will return the value
stored in the environment (if you do not tell **Confgetti** otherwise.).  
**Confgetti** does not punish you if you do not have the Consul server running, it will still return value from the environment variable!

Slightly *high-level* function [load_and_validate_config](#confgettiload_and_validate_configconfig_module_name-env_var-schemanone-keysnone-uppercasefalse), that is used for fetching multiple variables at once and overriding declared module variables, will try to get variable from one extra
source, the local JSON configuration file in the following order:

**Consul**  
⬇️   
**config.json**  
⬇️  
**environment**  
⬇️  
App

With the same *override* logic.


## [Consul settings](#consul-settings)

**Confgetti** uses a [python-consul](https://python-consul.readthedocs.io/en/latest/) package for communication with Consul's KV store.

Default connection settings are:

host: **consul**  
port: **8500**  
scheme: **http**  

Connection settings can be configured in **2** ways:

### [Through environment variables](#through-environment-variables)

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
all you need to set the following environment variables:

```
CONSUL_HOST=my_host
CONSUL_PORT=7500
CONSUL_SCHEME=https
``` 

And you do not have to pass any configuration dictionary when initializing Confgetti, because
it will read settings from the environment.

```python
# my_app/config.py
from Confgetti import get_variable

cgtti = Confgetti()

my_variable = cgtti.get_variable('MY_VARIABLE')
```

> **!!!ALERT:** This is only way of configuration for `load_and_validate_config` shorthand use.

### [Upon initialization](#upon-initialization)

When initializing **Confgetti** instance you can pass a dictionary with **Consnul** connection settings.

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

## [API](#api)

### [Shorthand methods](#shorthand-methods)

> **!!!ALERT:** If you are using shorthand functions, make sure that you have provided **Consul** connection settings via environment variables!
 
#### [confgetti.get_variables(path, keys, use_env=True, use_consul=True)](#confgettiget_variablespath-keys-use_envtrue-use_consultrue)

This is shorthand function for `confgetti.Confgetti.get_variables`.
Used for fetching multiple variables at once from **Consul** or environment. Returns dictionary for fetched variables.

**Arguments:**  
- **path**(optional) - Namespace of variable location inside **Consul** KV storage. By default as `None`, it looks to root of KV for the variable.
- **keys** - list of keys under which variables are defined. This can be a plain `list` of names, or `dict` where the key is the key name of variable and value type of value that should be returned. By default, variables are returned as a **string**. Available types: `str`, `int`, `bool`, `float`, `dict`. For example:

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

#### [confgetti.load_and_validate_config(config_module_name, env_var, schema=None, keys=None, uppercase=False)](#confgettiload_and_validate_configconfig_module_name-env_var-schemanone-keysnone-uppercasefalse)

Used for overriding current module variables. Usually it is used with [voluptuous.Schema](http://alecthomas.github.io/voluptuous/docs/_build/html/index.html) as `schema` argument for validation, but can be used without it, or with some custom method.

**Arguments:**  
- **config_module_name** - Usually `__name__` variable from current configuration file  
- **env_var** - Prefix of variables in the environment, the namespace of variables location in **CONSUL** and key under which `JSON` configuration path is stored in the environment. See the example for better understanding.  
- **schema**(optional) - Pass custom method here that should return `dict` of variables which will be glued to module later. Usually used with [voluptuous.Schema](http://alecthomas.github.io/voluptuous/docs/_build/html/index.html).  
- **keys**(optional) - variable names list or dict with the desired type. If you do not pass this, and you pass `voluptuous.Schema` under `schema` argument, the method will return variables declared dict passed to `Schema` instance.  
- **uppercase**(optional) - By default, variables are *glued* to the module in lowercase. If this is passed as `True`, variables will be *glued* in uppercase.  

**Example:**  

- *variables must be defined under `MY_APP` namespace in consul*
- *if `configuration.json` is used, environment variable `MY_APP` must be set with a path to the file

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

print(my_variable)  # should be a string and not None
print(your_variable  # should be an integer and not None

```

### [confgetti.Confgetti(consul_config=None, prepare_consul=True)](#confgetticonfgetticonsul_confignone-prepare_consultrue)

Confgetti intialization accepts two optional arguments, both refering to communication
with Consul.

**Arguments:** 
- **consul_config**(optional) - if dictionary with connection settings is passed client for communication with consul is initialized wit these settings.

    **Example:**  

    ```python
    from confgetti import Confgetti

    cgtti = Confgetti({
        'host': 'localhost'
    })
    ```

- **prepare_consul**(optional) - if `False` is passed, connection to Consul instance is not prepared, and Confgetti will only seek for variables in environment.

    **Example:**  

    ```python
    from confgetti import Confgetti

    cgtti = Confgetti(prepare_consul=False)

    cggti.get_variable('my_variable') # only environment lookup
    ```

#### [confgetti.Confgetti.get_variable(key, path=None, fallback=None, convert_to=None, use_env=True, use_consul=True)](#confgetticonfgettiget_variablekey-pathnone-fallbacknone-convert_tonone-use_envtrue-use_consultrue)

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

#### [confgetti.Confgetti.get_variables(path=None, keys=None, use_env=True, use_consul=True)](#confgetticonfgettiget_variablespathnone-keysnone-use_envtrue-use_consultrue)

This is internal method that is used for [get_variables](#confgettiget_variablespath-keys-use_envtrue-use_consultrue) shorthand. Arguments and logic is exactly the same.

**Example:**  

```python
from confgetti import Confgetti

cgtti = Confgetti()

my_variable = cgtti.get_variables(['my_variable', 'your_variable'])
```

## [Demos](#demos)

Check [demos](https://github.com/Styria-Digital/confgetti/tree/master/demos) folder for example usages as simple python scripts.

## [Developer Notes](#developer-notes)

### [Releasing new version](#releasing-new-version)

This repository has automatic deployment configured via CI runner.

**Steps for automatic deployment to `Styria`'s PyPI server:**  
1. Update `CHANGELOG.md` with future version release notes
2. Commit and push changelog to `master` branch
3. From the root of repository run `bumpversion patch`
4. Push changes that command in the previous step has made to the repo
5. Wait for `CI/CD` pipeline `deploy` step is finished, done!
