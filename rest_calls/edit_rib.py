import json
import syslog
import time
import os
import sys
from jinja2 import Environment, PackageLoader
from restClass import restCalls


# Probably delete these
username = ''
password = ''
ip_address = ''


def _prefixed(level, message):
    now = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
    return "%s %-8s %-6d %s" % (now, level, os.getpid(), message)


def render_config(update_json):
    """Take a exa command and translate it into yang formatted JSON
    :param update_json: The exa bgp string that is sent to stdout
    :type update_json: str

    """
    if 'announce' in update_json['neighbor']['message']['update']:
        prefixes = update_json['neighbor']['message']['update']['announce']['ipv4 unicast'].values()
        next_hop = update_json['neighbor']['message']['update']['announce']['ipv4 unicast'].keys()[0]
        # set env variable for jinja2
        env = Environment(loader=PackageLoader('edit_rib', 'templates'))
        env.filters['to_json'] = json.dumps
        template = env.get_template('static.json')
        rib_announce(template.render(next_hop=next_hop, data=prefixes))
    elif 'withdraw' in update_json['neighbor']['message']['update']:
        prefixes = update_json['neighbor']['message']['update']['withdraw']['ipv4 unicast'].keys()
        current_config = get_config()
        partial_config = current_config['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix']
        for whole_dictionary in partial_config:
            current_prefix = whole_dictionary.get('prefix')
            for exa_prefix in prefixes:
                exa_prefix, pre_length = exa_prefix.split('/')
                if exa_prefix == current_prefix:
                    partial_config.remove(whole_dictionary)
                    break
        current_config['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix'] = partial_config
        rib_withdraw(current_config)


def rib_announce(rendered_config):
        """Add networks to the RIB table.

        :param rendered_config: Jinja2 rendered configuration file
        :type rendered_config: unicode

        """
        rest_object = restCalls(username, password, ip_address)
        response = rest_object.patch(rendered_config)
        print response.status_code
#        status = response.status_code
#        syslog.syslog(syslog.LOG_ALERT, _prefixed('INFO', status))


def rib_withdraw(new_config):
    """Take newly created configuration file and PUT it.
        This will overwrite the previous config with the new one.

        :param new_config: The new RIB configuration
        :type new_config: str
    """
    rest_object = restCalls(username, password, ip_address)
    response = rest_object.put(new_config)
    status = response.status_code
    syslog.syslog(syslog.LOG_ALERT, _prefixed('INFO', status))


def get_config():
    """Grab the current RIB config off of the box

        :return: return the json HTTP response object
        :rtype: unicode string --check this?
    """
    rest_object = restCalls(username, password, ip_address)
    response = rest_object.get('Cisco-IOS-XR-ip-static-cfg:router-static/default-vrf/address-family/vrfipv4/vrf-unicast/vrf-prefixes/vrf-prefix')
    if not response.raise_for_status():
        return response.json()
    else:
        # needs to be tested
        error = response.raise_for_status()
        syslog.syslog(syslog.LOG_ALERT, _prefixed('ERROR', error))

'''
def update_watcher():
    """Watches for BGP updates from neighbors and triggers RIB change."""
    while True:
        raw_update = sys.stdin.readline().strip()
        update_json = json.loads(raw_update)
        if update_json['type'] == 'update':
            render_config(update_json)
            #update = sys.stdin.readline().strip()
'''


def tester():
    with open('/vagrant/BGP-filter/rest_calls/json.data', 'r') as f:
        fr = f.read()
        update_json = json.loads(fr)  # make json object python
        # A seperate RIB table change will be made for each update
        if update_json['type'] == 'update':
            render_config(update_json)

if __name__ == "__main__":
    tester()
