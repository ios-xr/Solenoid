"""Unit tests for checking rest calls. The tests are all mocked so no actual
calls are made to the router.
"""

import unittest
import os
import shutil

from mock import patch, call
from solenoid import edit_rib
from solenoid.tests import tools


class RestRibTestCase(unittest.TestCase, object):

    def setUp(self):
        #Set global variable
        edit_rib.FILEPATH = tools.add_location('examples/filter/filter-empty.txt')
        #Clear out logging files.
        open(tools.add_location('updates.txt'), 'w').close()
        open(tools.add_location('../logs/debug.log'), 'w').close()
        open(tools.add_location('../logs/errors.log'), 'w').close()
        # Move the config file so it doesn't get edited
        if os.path.isfile(tools.add_location('../../../solenoid.config')):
            os.rename(
                tools.add_location('../../solenoid.config'),
                tools.add_location('../../solenoidtest.config')
            )

    def tearDown(self):
        # If a new config file was created, delete it
        if os.path.isfile(tools.add_location('../../solenoid.config')):
            os.remove(tools.add_location('../../solenoid.config'))
        # If the config file was moved, move it back
        if os.path.isfile(tools.add_location('../../solenoidtest.config')):
            os.rename(
                tools.add_location('../../solenoidtest.config'),
                tools.add_location('../../solenoid.config')
            )

    def test_create_transport_object_correct_class_created(self):
        shutil.copy(
            tools.add_location('examples/config/restconf/restconf_good.config'),
            tools.add_location('../../solenoid.config')
        )
        transport_object = edit_rib.create_transport_object()
        self.assertIsInstance(transport_object, edit_rib.JSONRestCalls)

    def test_create_transport_object_no_config_file(self):
        with self.assertRaises(SystemExit):
            edit_rib.create_transport_object()
        self.assertIn('Something is wrong with your config file:',
                      tools.check_debuglog()[0])

    def test_create_transport_object_missing_object(self):
        shutil.copy(
            tools.add_location('examples/config/restconf/no_port.config'),
            tools.add_location('../../solenoid.config')
        )
        with self.assertRaises(SystemExit):
            edit_rib.create_transport_object()
        self.assertIn('Something is wrong with your config file:',
                      tools.check_debuglog()[0])

    def test_create_transport_object_missing_section(self):
        shutil.copy(
            tools.add_location('examples/config/restconf/no_section.config'),
            tools.add_location('../../solenoid.config')
        )
        with self.assertRaises(SystemExit):
            edit_rib.create_transport_object()
        self.assertIn('Something is wrong with your config file:',
                      tools.check_debuglog()[0])

    def test_create_transport_object_multiple_sections(self):
        shutil.copy(
            tools.add_location('examples/config/restconf/multiple_sections.config'),
            tools.add_location('../../solenoid.config')
        )
        transport_object = edit_rib.create_transport_object()
        self.assertIsInstance(transport_object, edit_rib.JSONRestCalls)
        self.assertIn('Multiple routers not currently supported in the configuration file',
                      tools.check_debuglog()[0])

    @patch('solenoid.edit_rib.JSONRestCalls.patch')
    def test_rib_announce(self, mock_patch):
        shutil.copy(
            tools.add_location('examples/config/restconf/restconf_good.config'),
            tools.add_location('../../solenoid.config')
        )
        with open(tools.add_location('examples/rendered_announce.txt')) as f:
            rendered_announce = f.read()
        edit_rib.rib_announce(rendered_announce)
        mock_patch.assert_called_with(rendered_announce)
        self.assertIn('| ANNOUNCE | ', tools.check_debuglog()[0])

    @patch('solenoid.edit_rib.JSONRestCalls.delete')
    def test_rib_withdraw(self, mock_delete):
        withdraw_prefixes = ['1.1.1.8/32',
                     '1.1.1.5/32',
                     '1.1.1.7/32',
                     '1.1.1.9/32',
                     '1.1.1.2/32',
                     '1.1.1.1/32',
                     '1.1.1.6/32',
                     '1.1.1.3/32',
                     '1.1.1.10/32',
                     '1.1.1.4/32']
        shutil.copy(
            tools.add_location('examples/config/restconf/restconf_good.config'),
            tools.add_location('../../solenoid.config')
        )
        edit_rib.rib_withdraw(withdraw_prefixes)
        url = 'Cisco-IOS-XR-ip-static-cfg:router-static/default-vrf/address-family/vrfipv4/vrf-unicast/vrf-prefixes/vrf-prefix='
        comma_list = [prefix.replace('/', ',') for prefix in withdraw_prefixes]
        calls = map(call, [url+x for x in comma_list])
        mock_delete.assert_has_calls(calls, any_order=True)
        self.assertIn('| WITHDRAW | ', tools.check_debuglog()[0])

if __name__ == '__main__':
    unittest.main()
