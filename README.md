# CONFGETTI

[![pipeline status](https://gl.sds.rocks/GDNI/confgetti/badges/master/pipeline.svg)](https://gl.sds.rocks/GDNI/confgetti/commits/master)
[![coverage report](https://gl.sds.rocks/GDNI/confgetti/badges/master/coverage.svg)](https://gl.sds.rocks/GDNI/confgetti/commits/master)

#### Tool for configuration and variables managment.

Fetch variables for your application easily from **Consul KV** -> **config\*.json**-> **environment.** via simple python method/s!


## The problem

Modern web app development and deployment oftenly considers isolated app enviroments which are easily manageble, and quickly delpoyed with software as VMs or Docker.

Everything hardens ands slows down as your app gets bigger and needs more and more *settings* variables declared in you configuration modules or classes, especially for those who manage production state of app or multiple apps. 

Lets call them DevOps.

Imagine simple web application that uses database for data storage, cache mechanism and AWS S3 Bucket static file storage. Oh yes, and our app is Dockerized.

To run that app successfully usually you need to pass configruation variables to methods/drivers that are communicating with those services. So at least, you'll need:

1. Database
    1. Database name
    2. Host
    3. Username
    4. Password
    5. Port?
2. Cache
    1. Host
    2. Index?
    3. Username?
    4. Password?
3. S3 Bucket
    1. AWS secret access key
    2. AWS access key id
    3. Bucket name

So for just 3 external services we could have up to 12 different settings variables that are crucial for successful running of our simple web app.

How you deal a problem like a noob?

#### 1. "King of n00bs" way

You could always leave those variable hardcoded to your configruation module, but prehaps, what if suddenly you need to switch to different AWS user and use different bucket? 

We even did not touched application code or logic actually but we need to:
1. push those changes to our repository (wait for Merge request, eh?)
2. build new Docker image
3. deploy new image

Whole deployment process just because  of those 3 simple variables. Not to mention that there are some sensitive data in those 12 variables,so storing them inside codebase is **NEVER** a good idea and **ALWAYS** security issue.

#### 2. "Slightly less n00b" way

Most common way of variables management, especially in Docker world, is to assign necessary varibles into container environment via Docker runner and then getting them from application by checking value of some agreed and known environment key name.

If we put aside security problem of such approach (yes, environment variables could be readable by malicious user), there is still one more common and frustrating problem: A bunch of sensitive variables that need to be correctly passed each time as our Docker container is restarted or redeployed.

Each time you need to pass those 12 variables to `docker` command, and even with `docker-compose` you still need to declare those variables in `docker-compose.yml` file which returns us to previous **"King of n00bs" way**.

Here we have just one simple web app, imagine size of problem on some cluster of web apps. Your DevOps(oftenly you) will hate you.

