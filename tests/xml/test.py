"""Tests the restClass module.

    You should comment out all the tests for restCalls that you are not testing
    at that moment, as they can interfere with each other. Sometimes status
    messages may change, for example, both 200 and 204 are successful messages.
    204 indicates that the call worked, there was just no content to be
    returned.

    Fill in your own username, password, ip address and port, and data source.
"""

import unittest
from rest_calls.xmlRestClass import XMLRestCalls


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


if __name__ == '__main__':
    unittest.main()
