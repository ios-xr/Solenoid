"""These unit tests test the functionality of each function, not the full program."""
import unittest
import os
import ConfigParser
from rest_calls.jsonRestClient import JSONRestCalls

here = os.path.dirname(os.path.realpath(__file__))
config = ConfigParser.ConfigParser()
config.read(os.path.join(here, 'restcalls.config'))
ip = config.get('default', 'ip')
port = int(config.get('default', 'port'))
username = config.get('default', 'username')
password = config.get('default', 'password')
endpoint = 'Cisco-IOS-XR-ipv4-ospf-cfg:ospf'
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

    def test_get(self):
        res = self.classObject.get()
        self.assertEqual(res.status_code, 200)

    def test_put_good_data(self):
        # Tests it with good data
        with open(os.path.join(here, '../examples/json/put_data.json')) as f:
            contents = f.read()
        res = self.classObject.put(contents, endpoint)
        self.assertEqual(res.status_code, 204)

    def test_put_bad_data(self):
        # Test it with bad data
        with open(os.path.join(here, '../examples/json/invalid_data.json')) as f:
            contents = f.read()
        put_res = self.classObject.put(contents, endpoint)
        self.assertEqual(put_res.status_code, 400)

    def test_patch_good_data(self):
        with open(os.path.join(here, '../examples/json/patch_data.json')) as f:
            contents = f.read()
        res = self.classObject.patch(contents, endpoint)
        self.assertEqual(res.status_code, 204)

    def test_patch_bad_data(self):
        with open(os.path.join(here, '../examples/json/invalid_data.json')) as f:
            contents = f.read()
        res = self.classObject.patch(contents, endpoint)
        self.assertEqual(res.status_code, 400)

    def test_post_good_data(self):
        with open(os.path.join(here, '../examples/json/put_data.json')) as f:
            contents = f.read()
        res = self.classObject.post(contents, endpoint)
        self.assertEqual(res.status_code, 204)

    def test_post_bad_data(self):
        # Test it with bad data
        with open(os.path.join(here, '../examples/json/invalid_data.json')) as f:
            contents = f.read()
        res = self.classObject.post(contents, endpoint)
        self.assertEqual(res.status_code, 400)

    def test_delete(self):
        res = self.classObject.delete(endpoint)
        self.assertEqual(res.status_code, 204)


if __name__ == "__main__":
    unittest.main()
