"""This module contains a class for making RESTcalls with Python"""

from requests.auth import HTTPBasicAuth
import requests
import re
import sys


class restCalls(object):
    """This class creates RESTconf calls using python.

        :param username: Username for device login
        :param password: Password for device login
        :param ip_address_port: The ip address and port number for the device
        :type password: str
        :type username: str
        :type ip_address_port: str
    """
    def __init__(self, username, password, ip_address_port):
        self.auth = HTTPBasicAuth(username, password)
        self.ip_address_port = ip_address_port

    def put(self, data_file):
        """PUT RESTconf call
            :param data_file: JSON or XML file with config changes
            :type data_file: File object
            :return: Return the response object
            :rtype: Response object
        """
        headers = self.create_headers(data_file)
        response = requests.put(url=headers[0], headers=headers[1],
                                auth=self.auth, data=data_file)
        return response

    def post(self, data_file):
        """POST RESTconf call
            :param data_file: JSON or XML file with config changes
            :type data_file: File object
            :return: Return the response object
            :rtype: Response object
        """
        headers = self.create_headers(data_file)
        response = requests.put(url=headers[0], headers=headers[1],
                                auth=self.auth, data=data_file)
        return response

    def patch(self, data_file):
        """PATCH RESTconf call
            :param data_file: JSON or XML file with config changes
            :type data_file: File object
            :return: Return the response object
            :rtype: Response object
        """
        headers = self.create_headers(data_file)
        response = requests.put(url=headers[0], headers=headers[1],
                                auth=self.auth, data=data_file)
        return response

    def get(self, choice):
        """GET RESTconf call
            :param choice: String selection of YANG model and local YANG
            :type choice: str
            :return: Return the response object
            :rtype: Response object
        """
        headers = self.create_headers(choice)
        url = headers[0] + "?content=config"
        response = requests.get(url=url, headers=headers[1],
                                auth=self.auth)
        return response

    def delete(self, choice):
        """GET RESTconf call
            :param choice: String selection of YANG model and container
            :type choice: str
            :return: Return the response object
            :rtype: Response object
        """
        headers = self.create_headers(choice)
        response = requests.delete(url=headers[0], headers=headers[1],
                                   auth=self.auth)
        return response

    def create_headers(self, data_source):
        """Generate the headers
            :param data_source: The file or yang model name
            :type data_source: Either a string or file object
            :return: Return a tuple with the header information
            :rtype: tuple

        """
        if isinstance(data_source, file):
            data_type = self.check_data_type(data_source)
            headers = ({
                'Accept': 'application/yang.errors+{}'.format(
                    data_type[0]),
                'Content-Type': 'application/yang.data+{}'.format(
                    data_type[0])
                })
            url = "http://{}/restconf/data/{}".format(
                self.ip_address_port, data_type[1])
        #If the second argument is a string it must be a GET or DELETE
        elif isinstance(data_source, str):
            url = "http://{}/restconf/data/{}".format(
                self.ip_address_port, data_source)
            headers = ({
                'Accept':
                'application/yang.data+json, application/yang.errors+json',
                'Content-Type': 'application/yang.data+json'
                })
        else:
            #If it isnt a file or a string something is wrong
            raise Exception("You need to enter a file or string.")
        return (url, headers)

    def check_data_type(self, data_source):
        """Check the data type of file and the YANG model

            :param data_source: The file with JSON or XML
            :type data_source: Open file object
            :return: Returns the type of data in the file and the
                     yang model name and local name
            :rtype: tuple(string, string)

        """
        #Grab the first two lines in the file
        line = [next(data_source) for x in xrange(2)]
        first_string = line[0]
        if first_string[:1] == '{' or first_string[:1] == '[':
            data_type = 'json'
            section = re.search(r'"(.*?)"', line[1])
            #If the data file only has the container name
            if re.match(r':', section.group(1)):
                return (data_type, section.group(1))
            else:
                module = raw_input("Please enter the YANG module name: ")
                section = module + ':' + section.group(1)
                return (data_type, section)
        elif first_string[:1] == '<':
            data_type = 'xml'
            section = re.search(r'<(.*?)>', line[0])
            if re.match(r':', section.group(1)):
                return (data_type, section.group(1))
            else:
                module = raw_input("Please enter the YANG module name: ")
                section = module + ':' + section.group(1)
                return (data_type, section)
        else:
            sys.exit("Your data file has malformed XML or JSON.")
