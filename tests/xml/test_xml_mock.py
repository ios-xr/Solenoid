import unittest

import mock
from requests import Response

from rest_calls.exceptions.exceptions import YangFileException
from rest_calls.xmlRestClass import XMLRestCalls


class XMLRestCallsCase(unittest.TestCase):
    def setUp(self):
        with open('/vagrant/rest_calls/tests/restcalls.config',
                  'r') as f:
            lines = f.readlines()
        self.username = lines[0].strip()
        self.password = lines[1].strip()
        self.ip_address = lines[2].strip()
        self.port = lines[3].strip()
        self.classObject = XMLRestCalls(self.ip_address, self.port,
                                        self.username, self.password)

    def test__init__(self):
        """Does constructor create a proper object"""
        headers = {
            'Accept': ','.join([
                'application/yang.data+xml',
                'application/yang.errors+xml',
                ]),
            'Content-Type': 'application/yang.data+xml',
            'Accept-Encoding': 'gzip, deflate, compress',
            'User-Agent': 'python-requests/2.2.1 CPython/2.7.6 Linux/3.13.0-68-generic'
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

    def test_get_endpoint(self):
        with open('/vagrant/rest_calls/examples/xml/put_data.xml',
                  'rb') as f:
            contents = f.read()
        yang_selection = self.classObject._get_endpoint(contents)
        self.assertEqual(yang_selection,
                         'Cisco-IOS-XR-ipv4-ospf-cfg:ospf')

        with open('/vagrant/rest_calls/examples/xml/missing_name_data.xml',
                  'rb') as f:
                bad_contents = f.read()
        with self.assertRaises(YangFileException):
                self.classObject._get_endpoint(bad_contents)

    @mock.patch('rest_calls.xmlRestClass.XMLRestCalls.get')
    def test_get(self, mock_get):
        mock_get.return_value = mock.MagicMock(spec=Response,
                                               status_code=200)
        get_res = self.classObject.get('bgp:bgp')

        mock_get.assert_called_once_with('bgp:bgp')
        self.assertEqual(get_res.status_code,
                         mock_get.return_value.status_code)

    @mock.patch('rest_calls.xmlRestClass.XMLRestCalls.put')
    def test_put(self, mock_put):
        with open('/vagrant/rest_calls/examples/xml/put_data.xml',
                  'rb') as f:
            contents = f.read()
        mock_put.return_value = mock.MagicMock(spec=Response,
                                               status_code=204)
        put_res = self.classObject.put(contents)
        mock_put.assert_called_once_with(contents)
        self.assertEqual(put_res.status_code,
                         mock_put.return_value.status_code)

    @mock.patch('rest_calls.xmlRestClass.XMLRestCalls.patch')
    def test_patch(self, mock_patch):
        with open('/vagrant/rest_calls/examples/xml/patch_data.xml',
                  'rb') as f:
            contents = f.read()
        mock_patch.return_value = mock.MagicMock(spec=Response,
                                                 status_code=204)
        patch_res = self.classObject.patch(contents)
        mock_patch.assert_called_once_with(contents)
        self.assertEqual(patch_res.status_code,
                         mock_patch.return_value.status_code)

    @mock.patch('rest_calls.xmlRestClass.XMLRestCalls.post')
    def test_post(self, mock_post):
        with open('/vagrant/rest_calls/examples/xml/put_data.xml',
                  'rb') as f:
            contents = f.read()
        mock_post.return_value = mock.MagicMock(spec=Response,
                                                status_code=204)
        post_res = self.classObject.post(contents)
        mock_post.assert_called_once_with(contents)
        self.assertEqual(post_res.status_code,
                         mock_post.return_value.status_code)

if __name__ == "__main__":
    unittest.main()
