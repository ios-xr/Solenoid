import unittest
import os
import json
import sys
import time

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
        edit_rib.filepath = os.path.join(location, 'examples/filter.txt')
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
        self.assertTrue('Not an update message type\n' in line)
        self.assertFalse(mock_render.called)

    @patch('sys.stdin', StringIO(_exa_raw('announce_g')))
    @patch('solenoid.edit_rib.update_validator')
    def test_update_watcher_call(self, mock_validator):
        # Monkey patching to avoid infinite loop.
        def mock_watcher():
            raw_update = sys.stdin.readline().strip()
            edit_rib.update_validator(raw_update)
        args = _exa_raw('announce_g')
        edit_rib.update_watcher = mock_watcher
        mock_watcher()
        mock_validator.assert_called_with(args)

    def test_update_file(self):
        edit_rib.update_file(
            {
                "Restart": time.ctime()
            }
        )
        with open(os.path.join(location, '../updates.txt')) as f:
            self.assertTrue(len(f.readlines()) == 1)

    # @patch('sys.stdin', StringIO(_exa_raw('announce_g')))
    # def test_announce_good(self):
    #     edit_rib.update_watcher()
    #     syslog = self._check_syslog()
    #     self.assertTrue(' 204\n' in syslog)

    # @patch('sys.stdin', StringIO(_exa_raw  ('announce_eor')))
    # def test_announce_eor(self):
    #     edit_rib.update_watcher()
    #     self.assertRaises(KeyError, edit_rib.update_watcher())

    # @patch('sys.stdin', StringIO(_exa_raw('withdraw_g')))
    # def test_withdraw_good(self):
    #     edit_rib.update_watcher()
    #     syslog = self._check_syslog()
    #     self.assertTrue(' 204\n' in syslog)

    # @patch('sys.stdin', StringIO(_exa_raw('withdraw_b')))
    # def test_withdraw_bad(self):
    #     edit_rib.update_watcher()
    #     syslog = self._check_syslog()
    #     self.assertTrue(' 409\n' in syslog)

    # @patch('sys.stdin', StringIO(_exa_raw('invalid_json')))
    # def test_invalid_json(self):
    #     self.assertRaises(ValueError, edit_rib.update_watcher())
    #     syslog = self._check_syslog()
    #     self.assertTrue('Failed JSON conversion for exa update\n' in syslog)

    # @patch('sys.stdin', StringIO(_exa_raw('invalid_n_model')))
    # def test_invalid_normal_model(self):
    #     self.assertRaises(ValueError, edit_rib.update_watcher())
    #     syslog = self._check_syslog()
    #     self.assertTrue('Extra data: ' in syslog)

    # @patch('sys.stdin', StringIO(_exa_raw('invalid_i_model')))
    # def test_invalid_incorect_model(self):
    #     self.assertRaises(ValueError, edit_rib.update_watcher())
    #     syslog = self._check_syslog()
    #     self.assertTrue('Expecting property ' in syslog)

if __name__ == '__main__':
    unittest.main()
