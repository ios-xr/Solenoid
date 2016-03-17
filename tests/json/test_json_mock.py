import unittest

import mock
from requests import Response

from rest.exceptions import YangFileException
from rest.jsonRestClass import JSONRestCalls


class JSONRestCallsCase(unittest.TestCase):
    def setUp(self):
        with open('/vagrant/bgp-filter/tests/restCalls.config',
                  'r') as f:
            lines = f.readlines()
        self.username = lines[0].strip()
        self.password = lines[1].strip()
        self.ip_address = lines[2].strip()
        self.port = lines[3].strip()
        self.classObject = JSONRestCalls(self.ip_address, self.port,
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

    @mock.patch('rest.jsonRestClass.JSONRestCalls.get')
    def test_get(self, mock_get):
        mock_get.return_value = mock.MagicMock(spec=Response,
                                               status_code=200)
        get_res = self.classObject.get('bgp:bgp')

        mock_get.assert_called_once_with('bgp:bgp')
        self.assertEqual(get_res.status_code,
                         mock_get.return_value.status_code)

    @mock.patch('rest.jsonRestClass.JSONRestCalls.put')
    def test_put(self, mock_put):
        with open('/vagrant/bgp-filter/examples/json/put_data.json',
                  'rb') as f:
            contents = f.read()
        mock_put.return_value = mock.MagicMock(spec=Response,
                                               status_code=204)
        put_res = self.classObject.put(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
        )
        mock_put.assert_called_once_with(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        self.assertEqual(put_res.status_code,
                         mock_put.return_value.status_code)

    @mock.patch('rest.jsonRestClass.JSONRestCalls.patch')
    def test_patch(self, mock_patch):
        with open('/vagrant/bgp-filter/examples/json/patch_data.json',
                  'rb') as f:
            contents = f.read()
        mock_patch.return_value = mock.MagicMock(spec=Response,
                                                 status_code=204)
        patch_res = self.classObject.patch(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        mock_patch.assert_called_once_with(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        self.assertEqual(patch_res.status_code,
                         mock_patch.return_value.status_code)

    @mock.patch('rest.jsonRestClass.JSONRestCalls.post')
    def test_post(self, mock_post):
        with open('/vagrant/bgp-filter/examples/json/put_data.json',
                  'rb') as f:
            contents = f.read()
        mock_post.return_value = mock.MagicMock(spec=Response,
                                                status_code=204)
        post_res = self.classObject.post(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        mock_post.assert_called_once_with(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        self.assertEqual(post_res.status_code,
                         mock_post.return_value.status_code)

if __name__ == "__main__":
    unittest.main()
