"""These unit tests test the functionality of each function, not the full program."""
import unittest
import os
import mock

from rest_calls.jsonRestClient import JSONRestCalls

here = os.path.dirname(os.path.realpath(__file__))


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
        headers = {
            'Accept': ','.join([
                'application/yang.data+json',
                'application/yang.errors+json',
                ]),
            'Content-Type': 'application/yang.data+json',
            'Accept-Encoding': 'gzip, deflate, compress',
            'User-Agent': 'python-requests/2.2.1 CPython/2.7.6 Linux/3.13.0-83-generic'
        }

        self.assertEqual(self.classObject._session.headers,
                         headers)
        self.assertEqual(self.classObject._host, self.url)

    @mock.patch('requests.sessions.Session.get')
    def test_get(self, mock_get):
        url = sm_url + 'bgp:bgp'
        self.classObject.get('bgp:bgp')
        mock_get.assert_called_once_with(url, params={})

    @mock.patch('requests.sessions.Session.put')
    def test_put_good_data(self, mock_put):
        # Tests it with good data
        with open(os.path.join(here, 'json/put_data.json')) as f:
            contents = f.read()
        url = sm_url + endpoint
        self.classObject.put(contents, endpoint)
        mock_put.assert_called_once_with(url, data=contents)

    # @mock.patch('requests.sessions.Session.put')
    # def test_put_bad_data(self, mock_put):
    #     # Test it with bad data
    #     with open(os.path.join(here, 'json/invalid_data.json')) as f:
    #         contents = f.read()
    #     put_res = mock_put(contents, 'bgp:bgp')
    #     self.assertEqual(put_res.status_code,
    #                      mock_put.return_value.status_code)

    @mock.patch('requests.sessions.Session.patch')
    def test_patch_good_data(self, mock_patch):
        with open(os.path.join(here, 'json/patch_data.json')) as f:
            contents = f.read()
        patch_res = mock_patch(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        mock_patch.assert_called_once_with(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        self.assertEqual(patch_res.status_code,
                         mock_patch.return_value.status_code)

    @mock.patch('rest_calls.jsonRestClient.JSONRestCalls.patch')
    def test_patch_bad_data(self, mock_patch):
        with open(os.path.join(here, 'json/invalid_data.json')) as f:
            contents = f.read()
        patch_res = mock_patch(contents, 'bgp:bgp')
        self.assertEqual(patch_res.status_code,
                         mock_patch.return_value.status_code)

    @mock.patch('rest_calls.jsonRestClient.JSONRestCalls.post')
    def test_post_good_data(self, mock_post):
        with open(os.path.join(here, 'json/put_data.json')) as f:
            contents = f.read()
        post_res = mock_post(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        mock_post.assert_called_once_with(
            contents,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        self.assertEqual(post_res.status_code,
                         mock_post.return_value.status_code)

    @mock.patch('rest_calls.jsonRestClient.JSONRestCalls.post')
    def test_post_bad_data(self, mock_post):
        # Test it with bad data
        with open(os.path.join(here, 'json/invalid_data.json')) as f:
            contents = f.read()
        post_res = mock_post(contents, 'bgp:bgp')
        self.assertEqual(post_res.status_code,
                         mock_post.return_value.status_code)


if __name__ == "__main__":
    unittest.main()
