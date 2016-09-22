import os
import unittest
import shutil
from solenoid import edit_rib

class TestBookends(unittest.TestCase, object):
    @classmethod
    def setUpClass(cls):
        #Silence stream logger.
        streamhandler = edit_rib.LOGGER._streamhandler
        streamhandler.close()
        edit_rib.LOGGER._logger.removeHandler(streamhandler)
        # Move the config file so it doesn't get edited
        if os.path.isfile(add_location('../../solenoid.config')):
            os.rename(
                add_location('../../solenoid.config'),
                add_location('../../solenoidtest.config')
            )
        shutil.copy(
            add_location('examples/config/restconf/restconf_good.config'),
            add_location('../../solenoid.config')
        )

    def setUp(self):
        #Set global variable.
        edit_rib.FILEPATH = add_location('examples/filter/filter-empty.txt')
        #Clear out logging files.
        open(add_location('../updates.txt'), 'w').close()
        open(add_location('../logs/debug.log'), 'w').close()
        open(add_location('../logs/errors.log'), 'w').close()

    @classmethod
    def tearDownClass(cls):
        # If a new config file was created, delete it
        if (os.path.isfile(add_location('../../solenoid.config'))
                and os.path.isfile(add_location('../../solenoidtest.config'))
           ):
            os.remove(add_location('../../solenoid.config'))
        # If the config file was moved, move it back
        if os.path.isfile(add_location('../../solenoidtest.config')):
            os.rename(
                add_location('../../solenoidtest.config'),
                add_location('../../solenoid.config')
            )

def exa_raw(test):
    with open(add_location('examples/exa/exa-raw.json')) as f:
        lines = f.readlines()
        if test == 'announce_g':
            exa_line = lines[0].strip()
        elif test == 'withdraw_g':
            exa_line = lines[1].strip()
        elif test == 'withdraw_b':
            exa_line = lines[2].strip()
        elif test == 'invalid_json':
            exa_line = lines[3].strip()
        elif test == 'invalid_n_model':
            exa_line = lines[4].strip()
        elif test == 'invalid_i_model':
            exa_line = lines[5].strip()
        elif test == 'announce_eor':
            exa_line = lines[6].strip()
        return exa_line

def check_errorlog():
    with open(add_location('../logs/errors.log')) as err_log:
        return err_log.readlines()

def check_debuglog():
    with open(add_location('../logs/debug.log')) as debug_log:
        return debug_log.readlines()

def add_location(filepath):
    location = os.path.dirname(os.path.realpath(__file__))
    new_filepath = os.path.join(location, filepath)
    return new_filepath
