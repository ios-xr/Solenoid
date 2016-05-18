import unittest
import os

from StringIO import StringIO
from mock import patch

from solenoid import edit_rib


class RibTestCase(unittest.TestCase):

    location = os.path.dirname(os.path.realpath(__file__))

    def setUp(self):
        edit_rib.filepath = os.path.join(self.location, 'examples/filter.txt')

    def _exa_raw(self, test):
        with open(os.path.join(self.location, 'examples/exa-raw.json')) as f:
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

    def test_announce_good(self):
        import pdb
        pdb.set_trace()
        with patch('sys.stdin', StringIO(self._exa_raw('announce_g'))):
            edit_rib.update_watcher()
        with open('/var/log/syslog', 'r') as syslog_f:
            # 1024 is relatively arbitrary
            syslog_f.seek(-1024, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue(' 204\n' in last)

    def test_announce_eor(self):
        with patch('sys.stdin', StringIO(self._exa_raw('announce_eor'))):
            edit_rib.update_watcher()
            self.assertRaises(KeyError, edit_rib.update_watcher())

    def test_withdraw_good(self):
        with patch('sys.stdin', StringIO(self._exa_raw('withdraw_g'))):
            edit_rib.update_watcher()
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue(' 204\n' in last)

    def test_withdraw_bad(self):
        with patch('sys.stdin', StringIO(self._exa_raw('withdraw_b'))):
            edit_rib.update_watcher()
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue(' 409\n' in last)

    def test_invalid_json(self):
        with patch('sys.stdin', StringIO(
                   self._exa_raw('invalid_json'))):
            self.assertRaises(ValueError, edit_rib.update_watcher())
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue('Failed JSON conversion for exa update\n' in last)

    def test_invalid_normal_model(self):
        with patch('sys.stdin', StringIO(
                   self._exa_raw('invalid_n_model'))):
            self.assertRaises(ValueError, edit_rib.update_watcher())
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue('Extra data: ' in last)

    def test_invalid_incorect_model(self):
        with patch('sys.stdin', StringIO(
                   self._exa_raw('invalid_i_model'))):
            self.assertRaises(ValueError, edit_rib.update_watcher())
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue('Expecting property ' in last)

if __name__ == '__main__':
    unittest.main()
