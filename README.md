# RESTconf Calls
##### Author: Lisa Roach
##### Email: lisroach@cisco.com

## Description:

A collection of python scripts implementing RESTconf calls. These scripts
utilize both Cisco and OpenConfig YANG modules. 

## Usage:

Be sure to change the username, password, and ip address/port in order
to run these scripts. 

To call a write method, choose either PUT, POST, PATCH, or DELETE. 

Create a JSON or XML file that contains the changes you want to make to
your device. 

On your command line, run (for everything except delete):

    $ python rest_write.py <your data filename> <your rest command>

Example:

    $ python rest_write.py data.json put
    $ python rest_write.py data.xml post

For DELETE, you do not need a JSON or XML file. Example:

    $ python rest_write delete

To call a get method, determine your YANG model. To see a list of options,
run:

    $ python rest_get.py options

    Example:

    $ python rest_get.py oc_bgp
    $ python rest_get.py cisco_isis
