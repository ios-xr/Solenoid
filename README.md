# RESTconf Calls
##### Author: Lisa Roach
##### Email: lisroach@cisco.com

## Description:

This repository contains a module for making RESTconf calls with python. 

You must add your ip address and port, username, and password for the 
constructor.

### Usage:


For PUT, POST, and PATCH, you must have a configuration of JSON or XML
formatted using a valid YANG model. If your device does not have the YANG
model available, you will not be able to use it. Examples of YANG models can be
found here:

OpenConfig: [https://github.com/openconfig/public]


YangModels: [https://github.com/YangModels/yang]

For GET and DELETE you must know the name of the YANG module and container that
you wish the make changes too. 

### Examples:

```
#PUT (works same for POST and PATCH)

rest_object = restCalls(username, password, ip_address_port)
response = rest_object.put(data)

```

```
#GET (same for DELETE)

rest_object = restCalls(username, password, ip_address_port)
response = rest_object.get('yang_module:container')

```
