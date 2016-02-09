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
    ip_address_port = 'ip_address:port'
    data_source = 'yang_module:container'

    def test_does_get_init_work(self):
        """Does constructor create a proper object"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        self.assertEqual(classObject.ip_address_port,
                         'ip_address:port')

    def test_check_data_json(self):
        """Test the check_data_type method for json"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as data_file:
            data_type = classObject.check_data_type(data_file)
            self.assertIsInstance(data_type, tuple)
            self.assertEqual(data_type[0], 'json')
            self.assertEqual(data_type[1].group(1), 'yang_module:container')

    def test_check_data_xml(self):
        """Test the check_data_type method for xml"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.xml', 'rb') as data_file:
            data_type = classObject.check_data_type(data_file)
            self.assertIsInstance(data_type, tuple)
            self.assertEqual(data_type[0], 'xml')
            self.assertEqual(data_type[1].group(1), 'yang_module:container')

    def test_header_creation(self):
        """Test the create_header method"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as data_file:
            items = classObject.create_headers(data_file)
            self.assertIsInstance(items, tuple)
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0], 'http://{}/restconf/data/yang_module:container'.format(
                             self.ip_address_port))
            self.assertEqual(items[1], ({
                'Accept':
                'application/yang.errors+json',
                'Content-Type': 'application/yang.data+json'
                }))

    def test_check_bad_json(self):
        """Test the check_data_type method for bad json"""
        with self.assertRaises(SystemExit) as cm:
            classObject = restCalls(self.username, self.password,
                                    self.ip_address_port)
            with open('bad_data.json', 'rb') as data_file:
                classObject.check_data_type(data_file)
        self.assertEqual(cm.exception.code,
                         "Your data file has malformed XML or JSON.")

    def test_check_bad_xml(self):
        """Test the check_data_type method for bad xml"""
        with self.assertRaises(SystemExit) as cm:
            classObject = restCalls(self.username, self.password,
                                    self.ip_address_port)
            with open('bad_data.xml', 'rb') as data_file:
                classObject.check_data_type(data_file)
            self.assertEqual(cm.exception.code,
                             "Your data file has malformed XML or JSON.")

    def test_get_request(self):
        """Test if GET returns a proper object"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        item = classObject.get('yang_module:container')
        self.assertIsInstance(item.content, str)
        #204 or 200 statuses are good
        self.assertEqual(item.status_code, 204)

    def test_put_request(self):
        """Test if PUT adds a configuration"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as data_file:
            item = classObject.put(data_file)
        self.assertEqual(item.status_code, 204)

    def test_post_request(self):
        """Test if POST adds a configuration"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as read_file:
            item = classObject.post(read_file)
        self.assertEqual(item.status_code, 201)

    def test_patch_request(self):
        """Test if PATCH adds a configuration"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        with open('data.json', 'rb') as read_file:
            item = classObject.patch(read_file)
        self.assertEqual(item.status_code, 204)

    def test_delete_request(self):
        """Test if DELETE removes the configuration"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port)
        item = classObject.delete('yang_mode:container')
        self.assertEqual(item.status_code, 200)

if __name__ == '__main__':
    unittest.main()
