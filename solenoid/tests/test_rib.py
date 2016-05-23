import unittest
import os
import json
import sys
import time
from netaddr import AddrFormatError

from StringIO import StringIO
from mock import patch

from solenoid import edit_rib


location = os.path.dirname(os.path.realpath(__file__))


def _exa_raw(test):
    with open(os.path.join(location, 'examples/exa-raw.json')) as f:
        lines = f.readlines()
        if test == 'announce_g':
            return lines[0].strip()
        elif test == 'withdraw_g':
            return lines[1].strip()
        elif test == 'withdraw_b':
            return lines[2].strip()
        elif test == 'invalid_json':
            return lines[3].strip()
        elif test == 'invalid_n_model':
            return lines[4].strip()
        elif test == 'invalid_i_model':
            return lines[5].strip()
        elif test == 'announce_eor':
            return lines[6].strip()


class RibTestCase(unittest.TestCase, object):

    def setUp(self):
        #Set global variable
        edit_rib.filepath = os.path.join(location, 'examples/filter-empty.txt')
        #Clear out logging files.
        open(os.path.join(location, '../updates.txt'), 'w').close()
        open(os.path.join(location, '../logs/debug.log'), 'w').close()
        open(os.path.join(location, '../logs/errors.log'), 'w').close()

    def _check_syslog(self):
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            return syslog_f.readlines()[-1]

    @patch('solenoid.edit_rib.render_config')
    def test_update_validator_good_json_conversion(self, mock_render):
        raw_g_json = _exa_raw('announce_g')
        args = json.loads(_exa_raw('announce_g'))
        edit_rib.update_validator(raw_g_json)
        mock_render.assert_called_with(args)

    @patch('solenoid.edit_rib.render_config')
    def test_update_validator_bad_json_conversion(self, mock_render):
        raw_b_json = _exa_raw('invalid_json')
        self.assertRaises(ValueError, edit_rib.update_validator(raw_b_json))
        # Check the logs.
        edit_rib.update_validator(raw_b_json)
        with open(os.path.join(location, '../logs/errors.log')) as log_f:
            line = log_f.readline()
        self.assertTrue('Failed JSON conversion for BGP update\n' in line)
        self.assertFalse(mock_render.called)

    @patch('solenoid.edit_rib.render_config')
    def test_update_validator_incorrect_model(self, mock_render):
        raw_b_json = _exa_raw('invalid_i_model')
        self.assertRaises(KeyError, edit_rib.update_validator(raw_b_json))
        # Check the logs.
        edit_rib.update_validator(raw_b_json)
        with open(os.path.join(location, '../logs/debug.log')) as log_f:
            line = log_f.readline()
        self.assertTrue('Not a valid update message type\n' in line)
        self.assertFalse(mock_render.called)

    def test_update_file(self):
        edit_rib.update_file(
            {
                'Restart': time.ctime()
            }
        )
        with open(os.path.join(location, '../updates.txt')) as f:
            self.assertTrue(len(f.readlines()) == 1)

    @patch('solenoid.edit_rib.rib_announce')
    def test_render_config_normal_model_missing_value(self, mock_announce):
        raw_json = _exa_raw('invalid_n_model')
        loaded_json = json.loads(raw_json)
        edit_rib.rib_announce = mock_announce
        #self.assertRaises(KeyError, edit_rib.render_config(loaded_json))
        edit_rib.render_config(loaded_json)
        with open(os.path.join(location, '../logs/debug.log')) as log_f:
            line = log_f.readline()
        self.assertTrue('Not a valid update message type\n' in line)
        self.assertFalse(mock_announce.called)

    @patch('solenoid.edit_rib.rib_announce')
    def test_render_config_normal_model_missing_value(self, mock_announce):
        formatted_json = json.loads(_exa_raw('invalid_n_model'))
        edit_rib.rib_announce = mock_announce
        self.assertRaises(KeyError, edit_rib.render_config(formatted_json))
        edit_rib.render_config(formatted_json)
        with open(os.path.join(location, '../logs/debug.log')) as log_f:
            line = log_f.readline()
        self.assertTrue('Not a valid update message type\n' in line)
        self.assertFalse(mock_announce.called)

    @patch('solenoid.edit_rib.rib_announce')
    def test_render_config_normal_model_eor(self, mock_announce):
        formatted_json = json.loads(_exa_raw('announce_eor'))
        edit_rib.rib_announce = mock_announce
        edit_rib.render_config(formatted_json)
        with open(os.path.join(location, '../logs/debug.log')) as log_f:
            line = log_f.readline()
        self.assertTrue('EOR message\n' in line)
        self.assertFalse(mock_announce.called)

    @patch('solenoid.edit_rib.rib_announce')
    def test_render_config_announce_good(self, mock_announce):
        formatted_json = json.loads(_exa_raw('announce_g'))
        edit_rib.render_config(formatted_json)
        with open(os.path.join(location, 'examples/rendered_announce.txt')) as f:
            rendered_announce = f.read()
        mock_announce.assert_called_with(rendered_announce)


    @patch('solenoid.edit_rib.rib_withdraw')
    def test_render_config_withdraw_good(self, mock_announce):
        formatted_json = json.loads(_exa_raw('withdraw_g'))
        edit_rib.render_config(formatted_json)
        mock_announce.assert_called_with('1.1.1.4/32')


    def test_filter_prefix(self):
        edit_rib.filepath = os.path.join(location, 'examples/filter-full.txt')
        start_prefixes = ['1.1.1.9/32', '192.168.3.1/28', '1.1.1.2/32', '1.1.1.1/32', '10.1.1.1/32', '1.1.1.10/32', '10.1.6.1/24']
        filtered_list = edit_rib.filter_prefixes(start_prefixes)
        end_prefixes = ['1.1.1.9/32', '1.1.1.2/32', '1.1.1.1/32', '1.1.1.10/32', '10.1.1.1/32']
        self.assertEqual(filtered_list, end_prefixes)


    def test_filter_prefix_invalid(self):
        edit_rib.filepath = os.path.join(location, 'examples/filter-invalid.txt')
        start_prefixes = ['1.1.1.9/32', '192.168.3.1/28', '1.1.1.2/32', '1.1.1.1/32', '10.1.1.1/32', '1.1.1.10/32', '10.1.6.1/24']
        import pdb
        pdb.set_trace()
        self.assertRaises(AddrFormatError, edit_rib.filter_prefixes(start_prefixes))



if __name__ == '__main__':
    unittest.main()
