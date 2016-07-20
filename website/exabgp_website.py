
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
from solenoid import CiscoGRPCClient

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def template_test():
    ip_address = request.form.get('ip_address', ' ')
    network = request.form.get('network', ' ')
    message = network + ' route ' + ip_address + ' next-hop self'
#    push_exabgp(message)
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

def push_exabgp(network, ip_address):
    #Push Network to Second ExaBGP instance, change URL to appropriate http api 
    message = network + ' route ' + ip_address + ' next-hop self' #Formats announcement got api
    url='http://192.168.1.3:55780' #Change this URL to your second exabgp instances HTTP api URL
    response = requests.post(url, data = {'command':message}, headers={'Content-Type':'application/x-www-form-urlencoded'})
    return


def get_rib():
    """Grab the current RIB config off of the box
        :return: return the json HTTP response object
        :rtype: dict
    """
    transport_object = create_transport_object()
    response = transport_object.get('{"Cisco-IOS-XR-ip-static-cfg:router-static": [null]}')
    return json.loads(response)

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
            if len(config.sections()) > 1:
                logger.warning('Multiple routers not currently supported in the configuration file. Using first router.', _source)
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
        logger.critical(
            'Something is wrong with your config file: {}'.format(
                e.message
            ),
            _source
        )
        sys.exit(1)

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

