import unittest
from restClass import restCalls


class restCallsCase(unittest.TestCase):
    username = 'username'
    password = 'password'
    ip_address_port = 'ip_address:port'
    data_source = 'bgp:bgp'

    def test_does_get_init_work(self):
        """Does constructor create a proper object for GET and DELETE"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port, self.data_source)
        self.assertEqual(classObject.url,
                         'http://10.200.96.52:2580/restconf/data/bgp:bgp')
        self.assertEqual(classObject.data_source, 'bgp:bgp')

    def test_check_data_json(self):
        """Test the check_data_type method for json"""
        with open('data.json', 'rb') as read_file:
            classObject = restCalls(self.username, self.password,
                                    self.ip_address_port, read_file)
            self.assertIsInstance(classObject.data_type, tuple)
            self.assertEqual(classObject.data_type[0], 'json')
            self.assertEqual(classObject.data_type[1].group(1), 'bgp:bgp')

    def test_check_data_xml(self):
        """Test the check_data_type method for xml"""
        with open('data.xml', 'rb') as read_file:
            classObject = restCalls(self.username, self.password,
                                    self.ip_address_port, read_file)
            self.assertIsInstance(classObject.data_type, tuple)
            self.assertEqual(classObject.data_type[0], 'xml')
            self.assertEqual(classObject.data_type[1].group(1), 'bgp:bgp')

    def test_check_bad_json(self):
        """Test the check_data_type method for bad json"""
        with open('bad_data.json', 'rb') as read_file:
            with self.assertRaises(SystemExit) as cm:
                restCalls(self.username, self.password,
                          self.ip_address_port, read_file)
            self.assertEqual(cm.exception.code,
                             "Your data file has malformed XML or JSON.")

    def test_check_bad_xml(self):
        """Test the check_data_type method for bad xml"""
        with open('bad_data.xml', 'rb') as read_file:
            with self.assertRaises(SystemExit) as cm:
                restCalls(self.username, self.password,
                          self.ip_address_port, read_file)
            self.assertEqual(cm.exception.code,
                             "Your data file has malformed XML or JSON.")

    def test_get_request(self):
        """Test if GET returns a proper object"""
        classObject = restCalls(self.username, self.password,
                                self.ip_address_port, self.data_source)
        item = classObject.get()
        self.assertIsInstance(item.content, str)

#    def test_put_request(self):
#        """Test if PUT adds a configuration"""
#        with open('data.json', 'rb') as read_file:
#            classObject = restCalls(self.username, self.password,
#                                    self.ip_address_port, read_file)
#            item = classObject.put()
#            self.assertEqual(item.status_code, 204)

    def test_post_request(self):
        """Test if POST adds a configuration"""
        with open('data.json', 'rb') as read_file:
            classObject = restCalls(self.username, self.password,
                                    self.ip_address_port, read_file)
            item = classObject.post()
            self.assertEqual(item.status_code, 201)

#    def test_patch_request(self):
#        """Test if PATCH adds a configuration"""
#        with open('data.json', 'rb') as read_file:
#            classObject = restCalls(self.username, self.password,
#                                    self.ip_address_port, read_file)
#            item = classObject.patch()
#            self.assertEqual(item.status_code, 204)

#    def test_delete_request(self):
#        """Test if DELETE removes the configuration"""
#        classObject = restCalls(self.username, self.password,
#                                self.ip_address_port, self.data_source)
#        item = classObject.delete()
#        self.assertEqual(item.status_code, 204)

if __name__ == '__main__':
    unittest.main()
