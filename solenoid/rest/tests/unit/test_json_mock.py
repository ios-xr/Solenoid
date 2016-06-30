"""These unit tests test the functionality of each function, not the full program."""
import unittest
import mock
import requests

from solenoid.rest.jsonRestClient import JSONRestCalls


username = 'admin'
password = 'admin'
ip = '127.0.0.1'
port = 80
endpoint = 'Cisco-IOS-XR-ip-static-cfg:router-static'
sm_url = '{scheme}://{ip}:{port}{basePath}/'.format(
    scheme='http',
    ip=ip,
    port=port,
    basePath='/restconf/data'
)
url = sm_url + endpoint
contents = '{test: test}'


class JSONRestCallsCase(unittest.TestCase):
    def setUp(self):
        self.classObject = JSONRestCalls(
            ip,
            port,
            username,
            password
        )

    def test__init__(self):
        """Does constructor create a proper object"""
        session = requests.Session()
        session.headers.update({
            'Accept': ','.join([
                'application/yang.data+json',
                'application/yang.errors+json',
                ]),
            'Content-Type': 'application/yang.data+json',
        })
        self.assertEqual(self.classObject._session.headers,
                         session.headers)
        self.assertEqual(self.classObject._host, sm_url)

    @mock.patch('requests.sessions.Session.get')
    def test_get(self, mock_get):
        self.classObject.get(endpoint)
        mock_get.assert_called_once_with(url, params={'content': 'config'})

    @mock.patch('requests.sessions.Session.put')
    def test_put(self, mock_put):
        self.classObject.put(contents, endpoint)
        mock_put.assert_called_once_with(url, data=contents)

    @mock.patch('requests.sessions.Session.patch')
    def test_patch(self, mock_patch):
        self.classObject.patch(contents, endpoint)
        mock_patch.assert_called_once_with(url, data=contents)

    @mock.patch('requests.sessions.Session.post')
    def test_post(self, mock_post):
        self.classObject.post(contents, endpoint)
        mock_post.assert_called_once_with(url, data=contents)

    @mock.patch('requests.sessions.Session.delete')
    def test_delete(self, mock_delete):
        self.classObject.delete(endpoint)
        mock_delete.assert_called_once_with(url)

if __name__ == "__main__":
    unittest.main()
