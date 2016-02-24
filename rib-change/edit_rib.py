import json
import syslog
import time
import os
import sys
from jinja2 import Environment, PackageLoader
from restClass import restCalls


def _prefixed(level, message):
    now = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
    return "%s %-8s %-6d %s" % (now, level, os.getpid(), message)


def render_config(update_json):
    """Take a exa command and translate it into yang formatted JSON
    :param update_json: The exa bgp string that is sent to stdout
    :type update_json: str

    """
    import pdb
    pdb.set_trace()
    if 'announce' in update_json['neighbor']['message']['update']:
        prefixes = update_json['neighbor']['message']['update']['announce']['ipv4 unicast'].values()
        next_hop = update_json['neighbor']['message']['update']['announce']['ipv4 unicast'].keys()[0]
        # set env variable for jinja2
        env = Environment(loader=PackageLoader('edit_rib', 'templates'))
        env.filters['to_json'] = json.dumps
        template = env.get_template('static.json')
        rib_announce(template.render(next_hop=next_hop, data=prefixes))
    elif 'withdraw' in update_json['neighbor']['message']['update']:
        yang_model = 'Cisco-IOS-XR-ip-static-cfg:vrf-prefixes'
        exa_prefixes = update_json['neighbor']['message']['update']['withdraw']['ipv4 unicast'].keys()
        # get the current RIB from the eXR
        current_config = get_config()
        # grab just the prefixes section
        partial_config = current_config[yang_model]['vrf-prefix']
        # values is the dictionary item in the vrf_prefix list
        for values in partial_config:
            current_prefix = values.get('prefix')
            # check the current prefix against the prefixes from exa
            for exa_prefix in exa_prefixes:
                exa_prefix, prefix_length = exa_prefix.split('/')
                if exa_prefix == current_prefix:
                    # if the current prefix is in the exa prefix list, remove
                    partial_config.remove(values)
                    break
        # update the current_config with its newly removed values
        current_config[yang_model]['vrf-prefix'] = partial_config
        rib_withdraw(current_config)


def create_rest_object():
    """Create a restCalls object.
        Reads in a file containing username, password, and
        ip address:port, in that order.

        :returns: restCalls object
        :rtype: restCalls class object
    """
    with open('/vagrant/BGP-filter/rest_calls/edit_rib.config', 'r') as f:
        lines = f.readlines()
    return restCalls(lines[0].replace("\r\n", ""),
                     lines[1].replace("\r\n", ""),
                     lines[2].replace("\r\n", ""))


def rib_announce(rendered_config):
        """Add networks to the RIB table.

        :param rendered_config: Jinja2 rendered configuration file
        :type rendered_config: unicode

        """
        rest_object = create_rest_object()
        response = rest_object.patch(rendered_config)
        status = response.status_code
        #syslog.syslog(syslog.LOG_ALERT, _prefixed('INFO', status))
        # for testing
        return status


def rib_withdraw(new_config):
    """Take newly created configuration file and PUT it.
        This will overwrite the previous config with the new one.

        :param new_config: The new RIB configuration
        :type new_config: str
    """
    rest_object = create_rest_object()
    # The put will rewrite the previous config
    response = rest_object.put(new_config)
    status = response.status_code
    #syslog.syslog(syslog.LOG_ALERT, _prefixed('INFO', status))
    # for testing
    return status


def get_config():
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


def update_watcher():
    """Watches for BGP updates from neighbors and triggers RIB change."""
    while True:
        # these two lines are just for testing purposes
        with open('json.dataw', 'r') as f:
            sys.stdin = f
        raw_update = sys.stdin.readline().strip()
        update_json = json.loads(raw_update)
        if update_json['type'] == 'update':
            render_config(update_json)


'''
def tester():
    with open('/vagrant/BGP-filter/rest_calls/json.dataw', 'r') as f:
        fr = f.read()
        update_json = json.loads(fr)  # make json object python
        # A seperate RIB table change will be made for each update
        if update_json['type'] == 'update':
            render_config(update_json)
'''

if __name__ == "__main__":
    tester()
