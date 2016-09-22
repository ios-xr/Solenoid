"""Unit tests for checking rest calls. The tests are all mocked so no actual
calls are made to the router.
"""

import unittest
import shutil

from mock import patch
from solenoid import edit_rib
from solenoid.tests import tools


class GRPCRibTestCase(tools.TestBookends, object):

    def test_create_transport_object_correct_class_created(self):
        shutil.copy(
            tools.add_location('examples/config/grpc/grpc_good.config'),
            tools.add_location('../../solenoid.config')
        )
        transport_object = edit_rib.create_transport_object()
        self.assertIsInstance(transport_object, edit_rib.CiscoGRPCClient)


    def test_create_transport_object_missing_object(self):
        shutil.copy(
            tools.add_location('examples/config/grpc/no_port.config'),
            tools.add_location('../../solenoid.config')
        )
        with self.assertRaises(SystemExit):
            edit_rib.create_transport_object()
        self.assertIn('Something is wrong with your config file:',
                      tools.check_errorlog()[0])

    def test_create_transport_object_missing_section(self):
        shutil.copy(
            tools.add_location('examples/config/grpc/no_section.config'),
            tools.add_location('../../solenoid.config')
        )
        with self.assertRaises(SystemExit):
            edit_rib.create_transport_object()
        self.assertIn('Something is wrong with your config file:',
                      tools.check_errorlog()[0])

    def test_create_transport_object_multiple_sections(self):
        shutil.copy(
            tools.add_location('examples/config/grpc/multiple_sections.config'),
            tools.add_location('../../solenoid.config')
        )
        transport_object = edit_rib.create_transport_object()
        self.assertIsInstance(transport_object, edit_rib.CiscoGRPCClient)
        self.assertIn('Multiple routers not currently supported in the configuration file',
                      tools.check_debuglog()[0])

    @patch('solenoid.edit_rib.CiscoGRPCClient.patch')
    def test_rib_announce(self, mock_patch):
        shutil.copy(
            tools.add_location('examples/config/grpc/grpc_good.config'),
            tools.add_location('../../solenoid.config')
        )
        with open(tools.add_location('examples/rendered_announce.txt')) as f:
            rendered_announce = f.read()
        edit_rib.transport = edit_rib.create_transport_object()
        edit_rib.rib_announce(rendered_announce, edit_rib.transport)
        mock_patch.assert_called_with(rendered_announce)
        self.assertIn('| ANNOUNCE | ', tools.check_debuglog()[0])

    @patch('solenoid.edit_rib.CiscoGRPCClient.delete')
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
            tools.add_location('examples/config/grpc/grpc_good.config'),
            tools.add_location('../../solenoid.config')
        )
        edit_rib.transport = edit_rib.create_transport_object()
        edit_rib.rib_withdraw(withdraw_prefixes, edit_rib.transport)
        url = '{{"Cisco-IOS-XR-ip-static-cfg:router-static": {{"default-vrf": {{"address-family": {{"vrfipv4": {{"vrf-unicast": {{"vrf-prefixes": {{"vrf-prefix": [{withdraw}]}}}}}}}}}}}}}}'
        prefix_info = '{{"prefix": "{bgp_prefix}","prefix-length": {prefix_length}}}'
        prefix_list = []
        for withdrawn_prefix in withdraw_prefixes:
            bgp_prefix, prefix_length = withdrawn_prefix.split('/')
            prefix_list += [
            prefix_info.format(
                bgp_prefix=bgp_prefix,
                prefix_length=prefix_length
                )
            ]
            prefix_str = ', '.join(prefix_list)
        url = url.format(withdraw=prefix_str)
        mock_delete.assert_called_once_with(url)
        self.assertIn('| WITHDRAW | ', tools.check_debuglog()[0])

if __name__ == '__main__':
    unittest.main()
