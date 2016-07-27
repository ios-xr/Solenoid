
''''This module is for starting a Flask website for exaBGP demo
Author: Karthik Kumaravel
Contact: kkumara3@cisco.com
'''

from flask import Flask, render_template, request, jsonify
import requests
import json
import sys
import os
import ConfigParser
from solenoid import JSONRestCalls

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/", methods=['GET', 'POST'])
def template_test():
    rib = get_rib()
    return render_template('index.html',
        Title = 'Solenoid Demo on IOS-XRv',
        content2 = rib,
        )
@app.route("/get_rib_json", methods=['GET'])
#Used for refreshing of object
def get_rib_json():
    return jsonify(get_rib())

@app.route("/get_exa_json", methods=['GET'])
#Used for refreshing of object
def get_exa_json():
    return get_exa()
@app.route("/prefix_change", methods=['GET'])
def prefix_change():
    prefix = request.args.get('ip_address')
    method = request.args.get('network')
    #Push Network to Second ExaBGP instance, change URL to appropriate http api
    here = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(here, '../filter.txt')
    if method == 'add':
        with open(filepath, 'a+') as filterf:
            found = False
            for line in filterf:
                if prefix in line:
                    raise InvalidUsage('Error cannot add: This prefix is already in the filter file.')
            if not found:
                filterf.write(prefix + '\n')
                filter_list = filterf.read()
                return filter_list
    elif method == 'remove':
        with open(filepath, 'r+') as filterf:
            found = False
            prefix_list = []
            for line in filterf:
                prefix_list.append(line)
            filterf.seek(0)
            for line in prefix_list:
                if line != prefix + '\n':
                    filterf.write(line)
                else:
                    found = True
            filterf.truncate()
            filter_list = filterf.read()
        if not found:
            raise InvalidUsage('Error cannot remove: The prefix was not in the prefix list')
        return filter_list
    else:
        with open(filepath) as filterf:
            filter_list = filterf.read()
            return filter_list



def get_rib():
    """Grab the current RIB config off of the box
        :return: return the json HTTP response object
        :rtype: dict
    """
    rest_object = create_rest_object()
    url = 'Cisco-IOS-XR-ip-static-cfg:router-static/default-vrf/'
    url += 'address-family/vrfipv4/vrf-unicast/vrf-prefixes/vrf-prefix'
    response = rest_object.get(url)
    if not response.raise_for_status():
        return response.json()
    else:
        # needs to be tested
        error = response.raise_for_status()
        syslog.syslog(syslog.LOG_ALERT, _prefixed('ERROR', error))


def create_rest_object():
    """Create a restCalls object.
        Replace IP_Address, Port, Username, and Password  in that order.
        :returns: restCalls object
        :rtype: restCalls class object
    """
    location = os.path.dirname(os.path.realpath(__file__))
    try:
        with open(os.path.join(location, '../solenoid.config')) as f:
            config = ConfigParser.ConfigParser()
            try:
                config.readfp(f)
                return JSONRestCalls(
                    config.get('default', 'ip'),
                    int(config.get('default', 'port')),
                    config.get('default', 'username'),
                    config.get('default', 'password')
                )
            except (ConfigParser.Error, ValueError), e:
                logger.critical(
                    'Something is wrong with your config file: {}'.format(
                        e.message
                    )
                )
                sys.exit(1)
    except IOError:
        logger.error('You must have a solenoid.config file.', _source)

def get_exa():
    #Opens file that announcements are stored and returns the last line
    with open('../solenoid/updates.txt', 'rb') as f: # change this to where the history.txt. file will be
        f.seek(-2,2)
        while f.read(1) != b"\n": # Until EOL is found...
            f.seek(-2, 1)         # ...jump back the read byte plus one more.
        last = f.readline()       # Read last line.
    return last



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=57780)


