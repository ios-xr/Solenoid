import unittest
import json
from solenoid import edit_rib
from solenoid.tests import tools



class RestRibTestCase(unittest.TestCase, object):
    def setUp(self):
        #Set global variable
        edit_rib.FILEPATH = tools.add_location('examples/filter-empty.txt')
        edit_rib.transport = edit_rib.create_transport_object()
        #Clear out logging files.
        open(tools.add_location('../updates.txt'), 'w').close()
        open(tools.add_location('../logs/debug.log'), 'w').close()
        open(tools.add_location('../logs/errors.log'), 'w').close()

    def test_rib_1announce(self):
        with open(tools.add_location('examples/integration/rendered_announce.txt')) as f:
            rendered_announce = f.read()
        edit_rib.rib_announce(rendered_announce, edit_rib.transport)
        self.assertIn('| ANNOUNCE | OK', tools.check_debuglog()[0])

    def test_rib_2withdraw(self):
        withdraw_prefixes = ['1.1.1.1/32',
                             '1.1.1.2/32',
                             '2.2.2.2/32',
                             '3.3.3.3/32']
        edit_rib.rib_withdraw(withdraw_prefixes, edit_rib.transport)
        self.assertIn('| WITHDRAW | OK', tools.check_debuglog()[0])

    def test_rib_3announce_json(self):
        with open(tools.add_location('examples/integration/exa-announce.json')) as f:
            exa_announce = f.read()
        edit_rib.render_config(json.loads(exa_announce), edit_rib.transport)
        self.assertIn('| ANNOUNCE | OK', tools.check_debuglog()[0])

    def test_rib_4withdraw_json(self):
        with open(tools.add_location('examples/integration/exa-withdraw.json')) as f:
            exa_withdraw = f.read()
        edit_rib.render_config(json.loads(exa_withdraw), edit_rib.transport)
        self.assertIn('| WITHDRAW | OK', tools.check_debuglog()[0])

    def test_rib_5announce_EOR(self):
        with open(tools.add_location('examples/exa/exa-eor.json')) as f:
            exa_announce_eor = f.read()
        edit_rib.render_config(json.loads(exa_announce_eor), edit_rib.transport)
        self.assertIn('EOR message\n', tools.check_debuglog()[0])
if __name__ == '__main__':
    unittest.main(failfast=True)
