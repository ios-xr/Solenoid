
''''This module is for starting a Flask website for exaBGP demo
Author: Karthik Kumaravel
Contact: kkumara3@cisco.com
'''

from flask import Flask, render_template, request, jsonify
import requests
import json
import sys
sys.path.append('/home/cisco/exabgp/bgp-filter/')
from rest.jsonRestClass import JSONRestCalls

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def template_test():
    ip_address = request.form.get('ip_address', ' ')
    network = request.form.get('network', ' ')
    message = network + ' route ' + ip_address + ' next-hop self'
#    push_exabgp(message)
    rib = get_rib()
    return render_template('index.html',
        Title = 'ExaBGP Demo on eXR Container',
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
    """Push Network to Second ExaBGP instance, change URL to appropriate http api
    """
    message = network + ' route ' + ip_address + ' next-hop self' #Formats announcement got api
    url='http://10.25.0.51:55780' #Change this URL to your second exabgp instances HTTP api URL
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
    return JSONRestCalls('10.1.1.5',
                     '80',
                     'vagrant',
                     'vagrant')
def get_exa():
    #Opens file that announcements are stored and returns the last line
    with open('/home/cisco/exabgp/history.txt', 'rb') as f:
        f.seek(-2,2)
        while f.read(1) != b"\n": # Until EOL is found...
            f.seek(-2, 1)         # ...jump back the read byte plus one more.
        last = f.readline()       # Read last line.
    return last



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=57780)

