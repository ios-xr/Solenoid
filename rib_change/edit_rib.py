import json
import syslog
import time
import os
import sys
import subprocess
from jinja2 import Environment, PackageLoader
from rest_calls.restClass import restCalls


def _prefixed(level, message):
    """Set the time, os pid, and the message in syslog format

        :param level: Level of syslog message
        :param message: Message to be printed to syslog
        :type level: str
        :type message: str

        return: string syslog output
        rtype: str
    """
    now = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
    return "%s %-8s %-6d %s" % (now, level, os.getpid(), message)


def render_config(update_json):
    """Take a exa command and translate it into yang formatted JSON

    :param update_json: The exa bgp string that is sent to stdout
    :type update_json: str

    """
    update_type = update_json['neighbor']['message']['update']
    if 'announce' in update_type:
        updated_prefixes = update_type['announce']['ipv4 unicast']
        prefixes = updated_prefixes.values()
        next_hop = updated_prefixes.keys()[0]
        # set env variable for jinja2
        env = Environment(loader=PackageLoader('rib_change', 'templates'))
        env.filters['to_json'] = json.dumps
        template = env.get_template('static.json')
        rib_announce(template.render(next_hop=next_hop, data=prefixes))
    elif 'withdraw' in update_type:
        exa_prefixes = update_type['withdraw']['ipv4 unicast'].keys()
        for withdrawn_prefix in exa_prefixes:
            rib_withdraw(withdrawn_prefix)


def create_rest_object():
    """Create a restCalls object.
        Reads in a file containing username, password, and
        ip address:port, in that order.

        :returns: restCalls object
        :rtype: restCalls class object
    """
    with open('/vagrant/BGP-filter/rib_change/edit_rib.config', 'r') as f:
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
        if status >= 200 and status < 300:  # Status code is good
            syslog.syslog(syslog.LOG_ALERT, _prefixed('INFO', status))
        else:
            syslog.syslog(syslog.LOG_ERR, _prefixed('ERROR', status))


def rib_withdraw(withdrawn_prefix):
    """Remove the withdrawn prefix from the RIB table

        :param new_config: The prefix and prefix-length to be removed
        :type new_config: str
    """
    rest_object = create_rest_object()
    exa_prefix, prefix_length = withdrawn_prefix.split('/')
    url = 'Cisco-IOS-XR-ip-static-cfg:router-static/default-vrf/'\
          'address-family/vrfipv4/vrf-unicast/vrf-prefixes/vrf-prefix='\
          '{},{}'.format(exa_prefix, prefix_length)
    response = rest_object.delete(url)
    status = response.status_code
    if status >= 200 and status < 300:  # Status code is good
        syslog.syslog(syslog.LOG_ALERT, _prefixed('INFO', status))
    else:
        syslog.syslog(syslog.LOG_ERR, _prefixed('ERROR', status))


def update_watcher():
    """Watches for BGP updates from neighbors and triggers RIB change."""
    while True:
        raw_update = sys.stdin.readline().strip()
        try:
            update_json = json.loads(raw_update)
        except ValueError, e:
            syslog.syslog(syslog.LOG_ERR, _prefixed('ERROR', e))
        else:
            if update_json['type'] == 'update':
                render_config(update_json)


def tester():
    with open('/vagrant/BGP-filter/examples/exa-announce.json', 'r') as f:
        fr = f.read()
        update_json = json.loads(fr)  # make json object python
        if update_json['type'] == 'update':
            render_config(update_json)


if __name__ == "__main__":
    tester()
