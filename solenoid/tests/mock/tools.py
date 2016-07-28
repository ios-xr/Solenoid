import os

def exa_raw(test):
    with open(add_location('../examples/exa/exa-raw.json')) as f:
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
    with open(add_location('../../logs/errors.log')) as err_log:
        return err_log.readlines()

def check_debuglog():
    with open(add_location('../../logs/debug.log')) as debug_log:
        return debug_log.readlines()

def add_location(filepath):
    location = os.path.dirname(os.path.realpath(__file__))
    new_filepath = os.path.join(location, filepath)
    return new_filepath