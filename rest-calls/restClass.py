"""This module contains a class for making RESTcalls with Python"""

from requests.auth import HTTPBasicAuth
import requests
import re
import sys
import json


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
        self._auth = HTTPBasicAuth(username, password)
        self._ip_address_port = ip_address_port

    def put(self, data):
        """PUT RESTconf call
            :param data: JSON or XML with config changes
            :type data: str
            :return: Return the response object
            :rtype: Response object
        """
        headers = self._create_headers_data(data)
        response = requests.put(url=headers[0], headers=headers[1],
                                auth=self._auth, data=data)
        return response

    def post(self, data):
        """POST RESTconf call
            :param data: JSON or XML file with config changes
            :type data: str
            :return: Return the response object
            :rtype: Response object
        """
        headers = self._create_headers_data(data)
        response = requests.post(url=headers[0], headers=headers[1],
                                 auth=self._auth, data=data)
        return response

    def patch(self, data):
        """PATCH RESTconf call
            :param data: JSON or XML with config changes
            :type data: str
            :return: Return the response object
            :rtype: Response object
        """
        headers = self._create_headers_data(data)
        response = requests.patch(url=headers[0], headers=headers[1],
                                  auth=self._auth, data=data)
        return response

    def get(self, choice):
        """GET RESTconf call
            :param choice: String selection of YANG model and local YANG
            :type choice: str
            :return: Return the response object
            :rtype: Response object
        """
        headers = self._create_headers_choice(choice)
        url = headers[0] + "?content=config"
        response = requests.get(url=url, headers=headers[1],
                                auth=self._auth)
        return response

    def delete(self, choice):
        """GET RESTconf call
            :param choice: String selection of YANG model and container
            :type choice: str
            :return: Return the response object
            :rtype: Response object
        """
        headers = self._create_headers_choice(choice)
        response = requests.delete(url=headers[0], headers=headers[1],
                                   auth=self._auth)
        return response

    def _create_headers_data(self, data_source):
        """Generate the headers
            :param data_source: The JSON or XML config
            :type data_source: str
            :return: Return a tuple with the header information
            :rtype: tuple

        """
        data_type = self._check_data_type(data_source)
        headers = ({
            'Accept': 'application/yang.errors+{}'.format(
                data_type[0]),
            'Content-Type': 'application/yang.data+{}'.format(
                data_type[0])
            })
        url = "http://{}/restconf/data/{}".format(
            self._ip_address_port, data_type[1])

        return (url, headers)

    def _create_headers_choice(self, data_source):
        """Generate the headers
            :param data_source: The yang model name
            :type data_source: str
            :return: Return a tuple with the header information
            :rtype: tuple

        """
        if type(data_source) == str:
            url = "http://{}/restconf/data/{}".format(
                self._ip_address_port, data_source)
            headers = ({
                'Accept':
                'application/yang.data+json, application/yang.errors+json'
                })
            return (url, headers)
        else:
            raise Exception("GET and DELETE require a string input.")

    def _check_data_type(self, data_source):
        """Check the data's type and the YANG model

            :param data_source: The JSON or XML
            :type data_source: str
            :return: Returns the type of data in the file and the
                     yang model name and local name
            :rtype: tuple(string, string)

        """
        try:
            json.loads(data_source)
            data_type = 'json'
            section = re.search(r'"(.*?)"', data_source[1:])
            #If the data file only has the container name
            if bool(re.search(r':', section.group(1))):
                return (data_type, section.group(1))
            else:
                module = raw_input("Please enter the YANG module name: ")
                section = module + ':' + section.group(1)
                return (data_type, section)
        except ValueError:
            if data_source[0] == "<":
                data_type = 'xml'
                section = re.search(r'<(.*?)>', data_source)
                if bool(re.search(r':', section.group(1))):
                    return (data_type, section.group(1))
                else:
                    module = raw_input("Please enter the YANG module name: ")
                    section = module + ':' + section.group(1)
                    return (data_type, section)
            else:
                sys.exit("Your data has malformed XML or JSON.")
