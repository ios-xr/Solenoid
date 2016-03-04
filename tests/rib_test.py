import unittest
import rib_change.edit_rib
from StringIO import StringIO
from mock import patch


class RibTestCase(unittest.TestCase):
    def _exa_raw(self, test):
        with open('/vagrant/BGP-filter/examples/exa-raw.json', 'r') as f:
            lines = f.readlines()
            if test == 'announce_g':
                return lines[0].strip()
            elif test == 'withdraw_g':
                return lines[1].strip()
            elif test == 'withdraw_b':
                return lines[2].strip()
            elif test == 'invalid_json':
                return lines[3].strip()
            elif test == 'invalid_model':
                return lines[4].strip()

    def test_announce_good(self):
        with patch('sys.stdin', StringIO(self._exa_raw('announce_g'))):
            rib_change.edit_rib.update_watcher()
        with open('/var/log/syslog', 'r') as syslog_f:
            # 1024 is relatively arbitrary
            syslog_f.seek(-1024, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue(' 204\n' in last)

    def test_withdraw_good(self):
        with patch('sys.stdin', StringIO(self._exa_raw('withdraw_g'))):
            rib_change.edit_rib.update_watcher()
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue(' 204\n' in last)

    def test_withdraw_bad(self):
        with patch('sys.stdin', StringIO(self._exa_raw('withdraw_b'))):
            rib_change.edit_rib.update_watcher()
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue(' 409\n' in last)

    def test_invalid_json(self):
        with patch('sys.stdin', StringIO(self._exa_raw('invalid_json'))):
            self.assertRaises(ValueError,
                              rib_change.edit_rib.update_watcher())
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue('No JSON object could be decoded\n' in last)

    def test_invalid_model(self):
        with patch('sys.stdin', StringIO(self._exa_raw('invalid_model'))):
            self.assertRaises(ValueError,
                              rib_change.edit_rib.update_watcher())
        with open('/var/log/syslog', 'r') as syslog_f:
            syslog_f.seek(-1060, 2)
            last = syslog_f.readlines()[-1]
        self.assertTrue('Expecting property ' in last)

if __name__ == '__main__':
    unittest.main()
