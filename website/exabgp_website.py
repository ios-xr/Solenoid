
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
from netaddr import IPNetwork, AddrFormatError
from solenoid import CiscoGRPCClient
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
    transport_object = create_transport_object()
    if isinstance(transport_object, CiscoGRPCClient):
        response = transport_object.get('{"Cisco-IOS-XR-ip-static-cfg:router-static": [null]}')
        return json.loads(response)
    else:
        response = transport_object.get('Cisco-IOS-XR-ip-static-cfg:router-static')
        return response.json()
def create_transport_object():
    """Create a grpc channel object.
        Reads in a file containing username, password, and
        ip address:port, in that order.
        :returns: grpc object
        :rtype: grpc class object
    """
    location = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.path.join(location, '../solenoid.config'))
        if len(config.sections()) >= 1:
            section = config.sections()[0]
            args = (
                config.get(section, 'ip'),
                int(config.get(section, 'port')),
                config.get(section, 'username'),
                config.get(section, 'password')
                )
            if config.get(section, 'transport').lower() == 'grpc':
                return CiscoGRPCClient(*args)
            if config.get(section, 'transport').lower() == 'restconf':
                return JSONRestCalls(*args)
        else:
            raise ValueError
    except (ConfigParser.Error, ValueError), e:
        sys.exit(1)

def get_exa():
    #Opens file that announcements are stored and returns the last line
    with open('../solenoid/updates.txt', 'rb') as f: # change this to where the history.txt. file will be
        f.seek(-2,2)
        while f.read(1) != b"\n": # Until EOL is found...
            f.seek(-2, 1)         # ...jump back the read byte plus one more.
        update = f.readline()       # Read last line.
    update = json.loads(update)
    time = update['time']
    peer_ip = update['neighbor']['ip']
    for key in update['neighbor']['message']['update'].keys():
        update_type = key
    for key in update['neighbor']['message']['update'][update_type]['ipv4 unicast'].keys():
        if update_type == 'announce':
            nexthop = key
            for key in update['neighbor']['message']['update'][update_type]['ipv4 unicast'][key].keys():
                network = key
        else:
            nexthop = ''
            network = key
    color = check_filter(network)
    exa = {}
    exa['time'] = time
    exa['peer_ip'] = peer_ip
    exa['update_type'] = update_type
    exa['nexthop'] = nexthop
    exa['network'] = network
    exa['color'] = color
    exa = json.dumps(exa)
    return exa

def check_filter(network):
    here = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(here, '../filter.txt')
    color = 'black'
    with open(filepath) as filterf:
        try:
            for line in filterf:
                if '-' in line:
                    # Convert it all to IPNetwork for comparison.
                    ip1, ip2 = line.split('-')
                    if IPNetwork(ip1) <= IPNetwork(network) <= IPNetwork(ip2):
                        color = 'black'
                    else:
                        color = 'red'
                else:
                    if IPNetwork(network) != IPNetwork(line):
                        color = 'red'
        except AddrFormatError, e:
            print e
    return color



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=57780)


