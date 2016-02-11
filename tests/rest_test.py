"""Tests the restClass module.

    You should comment out all the tests for restCalls that you are not testing
    at that moment, as they can interfere with each other. Sometimes status
    messages may change, for example, both 200 and 204 are successful messages.
    204 indicates that the call worked, there was just no content to be
    returned.

    Fill in your own username, password, ip address and port, and data source.
"""

import unittest
from restClass import restCalls


class restCallsCase(unittest.TestCase):
    username = 'username'
    password = 'password'
    ip_address_port = 'ip_address_port'
    data_choice = 'yang_module:container'

    def test_does_get_init_work(self):
        """Does constructor create a proper object"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        self.assertEqual(classObject.ip_address_port,
                         self.ip_address_port)

    def test_check_data_json(self):
        """Test the check_data_type method for json"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as data_file:
            contents = data_file.read()
            data_type = classObject.check_data_type(contents)
            self.assertIsInstance(data_type, tuple)
            self.assertEqual(data_type[0], 'json')
            self.assertEqual(data_type[1],
                             'yang_module:container')

    def test_check_data_xml(self):
        """Test the check_data_type method for xml"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.xml', 'rb') as data_file:
            contents = data_file.read()
            data_type = classObject.check_data_type(contents)
            self.assertIsInstance(data_type, tuple)
            self.assertEqual(data_type[0], 'xml')
            self.assertEqual(data_type[1], 'bgp:bgp')

    def test_header_creation_data(self):
        """Test the create_header_data method"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as data_file:
            contents = data_file.read()
            items = classObject.create_headers_data(contents)
            self.assertIsInstance(items, tuple)
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0],
                             'http://{}/restconf/data/{}'.format(
                                 self.ip_address_port, self.data_choice))
            self.assertEqual(items[1], ({
                'Accept':
                'application/yang.errors+json',
                'Content-Type': 'application/yang.data+json'
                }))

    def test_header_creation_choice(self):
        """Test the create_header_data method"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        items = classObject.create_headers_choice('bgp:bgp')
        self.assertIsInstance(items, tuple)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0], 'http://{}/restconf/data/bgp:bgp'.format(
                         self.ip_address_port))
        self.assertEqual(items[1], ({
            'Accept':
            'application/yang.data+json, application/yang.errors+json'
            }))

    def test_check_bad_json(self):
        """Test the check_data_type method for bad json"""
        with self.assertRaises(SystemExit) as cm:
            classObject = restCalls(self.username, self.password,
                                    self.ip_address_port)
            with open('bad_data.json', 'rb') as data_file:
                contents = data_file.read()
                classObject.check_data_type(contents)
        self.assertEqual(cm.exception.code,
                         "Your data has malformed XML or JSON.")

    def test_check_bad_xml(self):
        """Test the check_data_type method for bad xml"""
        with self.assertRaises(SystemExit) as cm:
            classObject = restCalls(self.username, self.password,
                                    self.ip_address_port)
            with open('bad_data.xml', 'rb') as data_file:
                contents = data_file.read()
                classObject.check_data_type(contents)
            self.assertEqual(cm.exception.code,
                             "Your data has malformed XML or JSON.")

    def test_get_request(self):
        """Test if GET returns a proper object"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        item = classObject.get('yang_module:conainer')
        self.assertIsInstance(item.content, str)
        #204 or 200 statuses are good
        self.assertEqual(item.status_code, 200)

    def test_incorrect_get_request(self):
        """Test if a bad GET request sends correct exception."""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with self.assertRaises(Exception):
            classObject.get(0)

    def test_put_request(self):
        """Test if PUT adds a configuration"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as data_file:
            contents = data_file.read()
            item = classObject.put(contents)
        self.assertEqual(item.status_code, 204)

    def test_post_request(self):
        """Test if POST adds a configuration"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as data_file:
            contents = data_file.read()
            item = classObject.post(contents)
        #204 or 201 are correct
        self.assertEqual(item.status_code, 201)

    def test_patch_request(self):
        """Test if PATCH adds a configuration"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as data_file:
            contents = data_file.read()
            item = classObject.patch(contents)
        #204 or 201 are correct
        self.assertEqual(item.status_code, 204)

    def test_delete_request(self):
        """Test if DELETE removes the configuration"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        item = classObject.delete('yang_module:container')
        #204 or 200 are correct
        self.assertEqual(item.status_code, 204)


if __name__ == '__main__':
    unittest.main()
