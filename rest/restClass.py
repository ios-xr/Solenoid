"""This module contains a class for making RESTcalls with Python"""

import requests
import abc
import logging


class RestCalls(object):
    """This class creates RESTconf calls using python.

        :param username: Username for device login
        :param password: Password for device login
        :param ip_address_port: The ip address and port number for the device
        :type password: str
        :type username: str
        :type ip_address_port: str
    """
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    __metaclass__ = abc.ABCMeta
    BasePath = '/restconf/data'
    Accept = [
        'application/yang.data+{fmt}',
        'application/yang.errors+{fmt}',
    ]
    ContentType = 'application/yang.data+{fmt}'

    def __init__(self, ip_address, port=80, username=None, password=None):
        session = requests.Session()
        if username is not None and password is not None:
            session.auth = (username, password)
        session.headers.update({
            'Accept': ','.join([
                accept.format(fmt=self.Format) for accept in self.Accept
            ]),
            'Content-Type': self.ContentType.format(fmt=self.Format),
        })
        self._session = session
        self._host = '{scheme}://{ip}:{port}{basePath}/'.format(
            scheme='http',
            ip=ip_address,
            port=port,
            basePath=self.BasePath
        )

    @abc.abstractmethod
    def _get_endpoint(data):
        pass

<<<<<<< HEAD
    def put(self, data, endpoint):
=======
    def lookup_code(self, code):
        """Look up the status code returned by a response object. """
        return requests.status_codes._codes.get(code)

    def put(self, data):
>>>>>>> master
        """PUT RESTconf call
            :param data: JSON or XML with config changes
            :type data: str
            :return: Return the response object
            :rtype: Response object
        """
        url = self._host + endpoint
        res = self._session.put(url, data=data)
        return res

    def post(self, data, endpoint):
        """POST RESTconf call
            :param data: JSON or XML file with config changes
            :type data: str
            :return: Return the response object
            :rtype: Response object
        """
        url = self._host + endpoint
        res = self._session.post(url, data=data)
        return res

    def patch(self, data, endpoint):
        """PATCH RESTconf call
            :param data: JSON or XML with config changes
            :type data: str
            :return: Return the response object
            :rtype: Response object
        """
        url = self._host + endpoint
        res = self._session.patch(url, data=data)
        return res

    def get(self, endpoint, **kwargs):
        """GET RESTconf call
            :param endpoint: String selection of YANG model and container
            :type endpoint: str
            :return: Return the response object
            :rtype: Response object
        """
        url = self._host + endpoint
        res = self._session.get(url, params=kwargs)
        return res

    def delete(self, endpoint):
        """GET RESTconf call
            :param endpoint: String selection of YANG model and container
            :type endpoint: str
            :return: Return the response object
            :rtype: Response object
        """
        url = self._host + endpoint
        res = self._session.delete(url)
        return res
