import unittest
import os
import ConfigParser

import mock
from requests import Response

from rest.jsonRestClient import JSONRestCalls


class JSONRestCallsCase(unittest.TestCase):
    def setUp(self):
        # Can be absolute or relative.
        obj = os.environ['BGP_FILTER_CONFIG']
        config = ConfigParser.ConfigParser()
        config.readfp(open(os.path.expanduser(obj)))
        self.ip = config.get('default', 'ip'),
        self.port = config.get('default', 'port'),
        self.username = config.get('default', 'username'),
        self.password = config.get('default', 'password')
        self.classObject = JSONRestCalls(self.ip, self.port,
                                         self.username, self.password)

    def test__init__(self):
        """Does constructor create a proper object"""
        headers = {
            'Accept': ','.join([
                'application/yang.data+json',
                'application/yang.errors+json',
                ]),
            'Content-Type': 'application/yang.data+json',
            'Accept-Encoding': 'gzip, deflate, compress',
            'User-Agent': 'python-requests/2.2.1 CPython/2.7.6 Linux/3.13.0-70-generic'
        }
        url = '{scheme}://{ip}:{port}{basePath}/'.format(
            scheme='http',
            ip=self.ip_address,
            port=self.port,
            basePath='/restconf/data'
        )
        self.assertEqual(self.classObject._session.headers,
                         headers)
        self.assertEqual(self.classObject._host, url)

    @mock.patch('rest.jsonRestClient.JSONRestCalls.get')
    def test_get(self, mock_get):
        mock_get.return_value = mock.MagicMock(spec=Response,
                                               status_code=200)
        get_res = self.classObject.get('bgp:bgp')

        mock_get.assert_called_once_with('bgp:bgp')
        self.assertEqual(get_res.status_code,
                         mock_get.return_value.status_code)

    @mock.patch('rest.jsonRestClient.JSONRestCalls.put')
    def test_put(self, mock_put):
        # Tests it with good data.
        location = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(location, 'examples/put_data.json'),
                  'rb') as f:
            contents = f.read()
        mock_put.return_value = mock.MagicMock(spec=Response,
                                               status_code=204)
        put_res = self.classObject.put(
            'Cisco-IOS-XR-ip-static-cfg:router-static',
            contents
        )
        mock_put.assert_called_once_with(
            'Cisco-IOS-XR-ip-static-cfg:router-static',
            contents
            )
        self.assertEqual(put_res.status_code,
                         mock_put.return_value.status_code)

        # Test it with bad data.
        location = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(location, 'examples/invalid_data.json'),
                  'rb') as f:
            contents = f.read()
        mock_put.return_value = mock.MagicMock(spec=Response,
                                               status_code=400)
        put_res = self.classObject.put('bgp:bgp', contents)
        self.assertEqual(put_res.status_code,
                         mock_put.return_value.status_code)

    @mock.patch('rest.jsonRestClient.JSONRestCalls.patch')
    def test_patch_good_data(self, mock_patch):
        location = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(location, 'examples/patch_data.json'),
                  'rb') as f:
            contents = f.read()
        mock_patch.return_value = mock.MagicMock(spec=Response,
                                                 status_code=204)
        patch_res = self.classObject.patch(
            'Cisco-IOS-XR-ip-static-cfg:router-static',
            contents
            )
        mock_patch.assert_called_once_with(
            'Cisco-IOS-XR-ip-static-cfg:router-static',
            contents
            )
        self.assertEqual(patch_res.status_code,
                         mock_patch.return_value.status_code)

    @mock.patch('rest.jsonRestClient.JSONRestCalls.patch')
    def test_patch_bad_data(self, mock_patch):
        location = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(location, 'examples/invalid_data.json'),
                  'rb') as f:
            contents = f.read()
        mock_patch.return_value = mock.MagicMock(spec=Response,
                                                 status_code=400)
        patch_res = self.classObject.put('bgp:bgp', contents)
        self.assertEqual(patch_res.status_code,
                         mock_patch.return_value.status_code)

    @mock.patch('rest.jsonRestClient.JSONRestCalls.post')
    def test_post(self, mock_post):
        location = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(location, 'examples/put_data.json'),
                  'rb') as f:
            contents = f.read()
        mock_post.return_value = mock.MagicMock(spec=Response,
                                                status_code=204)
        post_res = self.classObject.post(
            'Cisco-IOS-XR-ip-static-cfg:router-static',
            contents
            )
        mock_post.assert_called_once_with(
            'Cisco-IOS-XR-ip-static-cfg:router-static',
            contents
            )
        self.assertEqual(post_res.status_code,
                         mock_post.return_value.status_code)

        # Test it with bad data
        location = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(location, 'examples/invalid_data.json'),
                  'rb') as f:
            contents = f.read()
        mock_post.return_value = mock.MagicMock(spec=Response,
                                                status_code=400)
        put_res = self.classObject.put('bgp:bgp', contents)
        self.assertEqual(put_res.status_code,
                         mock_post.return_value.status_code)


if __name__ == "__main__":
    unittest.main()
