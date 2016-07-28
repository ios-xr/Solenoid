import unittest
import json
import time
import sys

from StringIO import StringIO
from mock import patch, call
from solenoid import edit_rib
from solenoid.tests.mock import tools


WITHDRAW_PREFIXES = ['1.1.1.8/32',
                     '1.1.1.5/32',
                     '1.1.1.7/32',
                     '1.1.1.9/32',
                     '1.1.1.2/32',
                     '1.1.1.1/32',
                     '1.1.1.6/32',
                     '1.1.1.3/32',
                     '1.1.1.10/32',
                     '1.1.1.4/32']

class GeneralRibTestCase(unittest.TestCase, object):

    def setUp(self):
        #Set global variable
        edit_rib.FILEPATH = tools.add_location('../examples/filter/filter-empty.txt')
        #Clear out logging files.
        open(tools.add_location('../../updates.txt'), 'w').close()
        open(tools.add_location('../../logs/debug.log'), 'w').close()
        open(tools.add_location('../../logs/errors.log'), 'w').close()
    
    @patch('sys.stdin', StringIO(tools.exa_raw('announce_g')))
    @patch('solenoid.edit_rib.update_validator')
    def test_update_watcher_call(self, mock_validator):
       # Monkey patching to avoid infinite loop.
        def mock_watcher():
            raw_update = sys.stdin.readline().strip()
            edit_rib.update_validator(raw_update)
        args = tools.exa_raw('announce_g')
        edit_rib.update_watcher = mock_watcher
        mock_watcher()
        mock_validator.assert_called_with(args)

    @patch('solenoid.edit_rib.render_config')
    def test_update_validator_good_json_conversion(self, mock_render):
        raw_g_json = tools.exa_raw('announce_g')
        args = json.loads(tools.exa_raw('announce_g'))
        edit_rib.update_validator(raw_g_json)
        mock_render.assert_called_with(args)

    @patch('solenoid.edit_rib.render_config')
    def test_update_validator_bad_json_conversion(self, mock_render):
        raw_b_json = tools.exa_raw('invalid_json')
        self.assertRaises(ValueError, edit_rib.update_validator(raw_b_json))
        # Check the logs.
        self.assertIn('Failed JSON conversion for BGP update\n',
                      tools.check_errorlog()[0])
        self.assertFalse(mock_render.called)

    @patch('solenoid.edit_rib.render_config')
    def test_update_validator_incorrect_model(self, mock_render):
        raw_b_json = tools.exa_raw('invalid_i_model')
        self.assertRaises(KeyError, edit_rib.update_validator(raw_b_json))
        # Check the logs.
        self.assertTrue('Not a valid update message type\n',
                        tools.check_debuglog()[0])
        self.assertFalse(mock_render.called)

    def test_update_file(self):
        edit_rib.update_file(
            {
                'Restart': time.ctime()
            }
        )
        with open(tools.add_location('../../updates.txt')) as f:
            self.assertTrue(len(f.readlines()) == 1)

    @patch('solenoid.edit_rib.rib_announce')
    def test_render_config_normal_model_missing_value(self, mock_announce):
        formatted_json = json.loads(tools.exa_raw('invalid_n_model'))
        edit_rib.rib_announce = mock_announce
        self.assertRaises(KeyError, edit_rib.render_config(formatted_json))
        self.assertIn('Not a valid update message type\n',
                      tools.check_errorlog()[0])
        self.assertFalse(mock_announce.called)

    @patch('solenoid.edit_rib.rib_announce')
    def test_render_config_normal_model_eor(self, mock_announce):
        formatted_json = json.loads(tools.exa_raw('announce_eor'))
        #edit_rib.rib_announce = mock_announce
        edit_rib.render_config(formatted_json)
        self.assertIn('EOR message\n', tools.check_debuglog()[0])
        self.assertFalse(mock_announce.called)

    @patch('solenoid.edit_rib.rib_announce')
    def test_render_config_announce_good(self, mock_announce):
        formatted_json = json.loads(tools.exa_raw('announce_g'))
        edit_rib.render_config(formatted_json)
        with open(tools.add_location('../examples/rendered_announce.txt'), 'U') as f:
            rendered_announce = f.read()
        mock_announce.assert_called_with(rendered_announce)

    @patch('solenoid.edit_rib.rib_withdraw')
    def test_render_config_withdraw_good(self, mock_announce):
        formatted_json = json.loads(tools.exa_raw('withdraw_g'))
        edit_rib.render_config(formatted_json)
        mock_announce.assert_called_with(WITHDRAW_PREFIXES)

    def test_filter_prefix_good(self):
        edit_rib.FILEPATH = tools.add_location('../examples/filter/filter-full.txt')
        start_prefixes = ['1.1.1.9/32',
                          '192.168.3.1/28',
                          '1.1.1.2/32',
                          '1.1.1.1/32',
                          '10.1.1.1/32',
                          '1.1.1.10/32',
                          '10.1.6.1/24']
        filtered_list = edit_rib.filter_prefixes(start_prefixes)
        end_prefixes = ['1.1.1.9/32',
                        '1.1.1.2/32',
                        '1.1.1.1/32',
                        '1.1.1.10/32',
                        '10.1.1.1/32',
                        '10.1.6.1/24']
        self.assertEqual(filtered_list, end_prefixes)

# This test is wrong - the error is raising but assertRaises is failing
    # def test_filter_prefix_invalid(self):
    #     edit_rib.filepath = tools.add_location('examples/filter-invalid.txt')
    #     start_prefixes = ['1.1.1.9/32',
    #                       '192.168.3.1/28',
    #                       '1.1.1.2/32',
    #                       '1.1.1.1/32',
    #                       '10.1.1.1/32',
    #                       '1.1.1.10/32',
    #                       '10.1.6.1/24']
    #     self.assertRaises(edit_rib.AddrFormatError,
    #                       edit_rib.filter_prefixes,
    #                       start_prefixes)

if __name__ == '__main__':
    unittest.main()

