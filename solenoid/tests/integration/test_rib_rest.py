import unittest
import os
import json
from solenoid import edit_rib

location = os.path.dirname(os.path.realpath(__file__))
withdraw_prefixes = ['1.1.1.1/32',
                     '1.1.1.2/32',
                     '2.2.2.2/32',
                     '3.3.3.3/32']

class RestRibTestCase(unittest.TestCase, object):
    def setUp(self):
        #Set global variable
        edit_rib.filepath = os.path.join(location, 'examples/filter-empty.txt')
        #Clear out logging files.
        open(os.path.join(location, '../../updates.txt'), 'w').close()
        open(os.path.join(location, '../../logs/debug.log'), 'w').close()
        open(os.path.join(location, '../../logs/errors.log'), 'w').close()

    def _check_errorlog(self):
        with open(os.path.join(location, '../../logs/errors.log')) as err_log:
            return err_log.readlines()

    def _check_debuglog(self):
        with open(os.path.join(location, '../../logs/debug.log')) as debug_log:
            return debug_log.readlines()
    def test_create_transport_object_correct_class_created(self):
        transportObject = edit_rib.create_transport_object()
        self.assertIsInstance(transportObject, edit_rib.JSONRestCalls)

    def test_rib_announce_rest(self):
        with open(os.path.join(location, '../examples/integration/rendered_announce.txt')) as f:
            rendered_announce = f.read()
        edit_rib.rib_announce(rendered_announce)
        self.assertIn('| ANNOUNCE | ', self._check_debuglog()[0])

    def test_rib_withdraw_rest(self):
        edit_rib.rib_withdraw(withdraw_prefixes)
        self.assertIn('| WITHDRAW | ', self._check_debuglog()[0])

    def test_rib_announce_rest_json(self):
        with open(os.path.join(location, '../examples/integration/exa-announce.json')) as f:
            exa_announce = f.read()
        edit_rib.render_config(json.loads(exa_announce))
        self.assertIn('| ANNOUNCE | ', self._check_debuglog()[0])

    def test_rib_withdraw_rest_json(self):
        with open(os.path.join(location, '../examples/integration/exa-withdraw.json')) as f:
            exa_withdraw = f.read()
        edit_rib.render_config(json.loads(exa_withdraw))
        self.assertIn('| WITHDRAW | ', self._check_debuglog()[0])

if __name__ == '__main__':
    unittest.main(failfast = True)

