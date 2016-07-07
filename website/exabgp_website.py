
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

