from requests.auth import HTTPBasicAuth
import requests
import re
import sys


class restCalls(object):
    def __init__(self, username, password, ip_address_port, data_source):
        self.auth = HTTPBasicAuth(username, password)
        self.data_source = data_source
        #Check the data file type if a file has been provided
        if isinstance(self.data_source, file):
            self.data_type = self.check_data_type()
            self.headers = ({
                'Accept': 'application/yang.errors+{}'.format(
                    self.data_type[0]),
                'Content-Type': 'application/yang.data+{}'.format(
                    self.data_type[0])
                })
            self.url = "http://{}/restconf/data/{}".format(
                ip_address_port, self.data_type[1].group(1))
        #If the second argument is a string it must be a GET or DELETE
        elif isinstance(self.data_source, str):
            self.url = "http://{}/restconf/data/{}".format(
                ip_address_port, self.data_source)
            self.headers = ({
                'Accept':
                'application/yang.data+json, application/yang.errors+json',
                'Content-Type': 'application/yang.data+json'
                })

    def put(self):
        response = requests.put(url=self.url, headers=self.headers,
                                auth=self.auth, data=self.data_source)
        return response

    def post(self):
        response = requests.post(url=self.url, headers=self.headers,
                                 auth=self.auth, data=self.data_source)
        return response

    def patch(self):
        response = requests.patch(url=self.url, headers=self.headers,
                                  auth=self.auth, data=self.data_source)
        return response

    def get(self):
        url = self.url + "?content=config"
        response = requests.get(url=url, headers=self.headers,
                                auth=self.auth)
        return response

    def check_data_type(self):
        """Check the data type of file and the YANG model

            :return: Returns the type of data in the file and the
                     yang model name
            :rtype: tuple(string, string)

        """
        line = [next(self.data_source) for x in xrange(2)]
        first_string = line[0]
        if first_string[:1] == '{' or first_string[:1] == '[':
            data_type = 'json'
            section = re.search(r'"(.*?)"', line[1])
            return (data_type, section)
        elif first_string[:1] == '<':
            data_type = 'xml'
            section = re.search(r'<(.*?)>', line[0])
            return (data_type, section)
        else:
            sys.exit("Your data file has malformed XML or JSON.")
