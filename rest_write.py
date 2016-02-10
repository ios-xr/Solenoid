"""
This module contains a single function that creates a rest change call.
Requires a command line argument specifying the json data file as well
as an argument choosing PUT, POST, or PATCH, unless you are deleting. If you are
deleting you do not need to add a json file, just use the 'delete' keyword.

Example:
    $ python rest_write.py data.json put
    $ python rest_write.py data.json post
    $ python rest_write.py delete

 """

import sys
from requests.auth import HTTPBasicAuth
import requests
import re


def rest_put_post():
    """Complete a REST POST or PUT based on the cli file and argument entered"""
    #Replace the username and password with your information
    auth = HTTPBasicAuth('username', 'password')
    if sys.argv[1] != 'delete':
            with open(sys.argv[1], 'rb') as read_file:
                data_type = check_data_type(read_file)
                #declare variables according to the data type
                myheaders = ({
                    'Accept': 'application/yang.errors+{}'.format(
                              data_type[0]),
                    'Content-Type': 'application/yang.data+{}'.format(
                             data_type[0])
                    })
                #Replace the <ip address:port> with your information
                url = "http://<ip address:port>/restconf/data/{}".format(
                      data_type[1].group(1))
                if sys.argv[2] == 'put':
                    response = requests.put(url=url,
                                            headers=myheaders,
                                            auth=auth,
                                            data=read_file)
                elif sys.argv[2] == 'post':
                    response = requests.post(url=url,
                                             headers=myheaders,
                                             auth=auth,
                                             data=read_file)
                elif sys.argv[2] == 'patch':
                    response = requests.patch(url=url,
                                              headers=myheaders,
                                              auth=auth,
                                              data=read_file)
    elif sys.argv[1] == 'delete':
        response = requests.delete(url=url,
                                   headers={
                                       'Accept': 'application/yang.errors+json',
                                       'Content-Type': 'application/yang.data+json'},
                                   auth=auth)
    else:
        print "You must define 'put', 'post, 'patch', or 'delete'."
        print "Example: python rest_write.py data.json put"
        print "Example: python rest_write.py delete"
        sys.exit()

    error = response.raise_for_status()
    if error == 'None' or response.status_code == 204:
        print "Success!"


def check_data_type(read_file):
    """Check the data type of file and the YANG model"""
    line = [next(read_file) for x in xrange(2)]
    first_string = line[0]
    if first_string[:1] == '{' or first_string[:1] == '[':
        data_type = 'json'
        section = re.search(r'"(.*?)"', line[1])
    elif first_string[:1] == '<':
        data_type = 'xml'
        section = re.search(r'"(.*?)"', line[1])
    else:
        data_type = 'error'
        section = 'error'
    return (data_type, section)

