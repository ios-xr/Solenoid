import json
import syslog
import time
import os
import sys
import logging
import logging.config
from jinja2 import Environment, PackageLoader
sys.path.append('/home/cisco/exabgp/bgp-filter/')
from rest.jsonRestClass import JSONRestCalls


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
    try:
        update_type = update_json['neighbor']['message']['update']
        if 'announce' in update_type:
            updated_prefixes = update_type['announce']['ipv4 unicast']
            prefixes = updated_prefixes.values()
            next_hop = updated_prefixes.keys()[0]
            # set env variable for jinja2
            env = Environment(loader=PackageLoader('rib_change',
                              'templates'))
            env.filters['to_json'] = json.dumps
            template = env.get_template('static.json')
            rib_announce(template.render(next_hop=next_hop,
                                         data=prefixes))
        elif 'withdraw' in update_type:
            exa_prefixes = update_type['withdraw']['ipv4 unicast'].keys()
            for withdrawn_prefix in exa_prefixes:
                rib_withdraw(withdrawn_prefix)
    except ValueError:  # If we hit an eor or other type of update
        logging.error('Failed JSON conversion for:\n %s \n',
                      update_json,
                      exc_info=True)
        pass


def create_rest_object():
    """Create a restCalls object.
        Reads in a file containing username, password, and
        ip address:port, in that order.

        This method could be eliminated and the restCalls(username, password,
        ip_address:port) replace all calls to create_rest_object().
        This method exists in order to seperate passwords from github.

        :returns: restCalls object
        :rtype: restCalls class object
    """
    with open('/vagrant/BGP-filter/rib_change/edit_rib.config', 'r') as f:
        lines = f.readlines()
    return JSONRestCalls(lines[0].replace("\r\n", ""),
                     lines[1].replace("\r\n", ""),
                     lines[2].replace("\r\n", ""))


def rib_announce(rendered_config):
        """Add networks to the RIB table using HTTP PATCH over RESTconf.

        :param rendered_config: Jinja2 rendered configuration file
        :type rendered_config: unicode

        """
        rest_object = create_rest_object()
        response = rest_object.patch(rendered_config)
        status = response.status_code
        if status >= 200 and status < 300:  # Status code is good
            logging.info('ANNOUNCE: %s %s',
                         status,
                         rest_object.lookup_code(status),
                         )
        else:
            logging.warning('ANNOUNCE: %s %s',
                            status,
                            rest_object.lookup_code(status),
                            )


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
        logging.info('WITHDRAW: %s %s',
                     status,
                     rest_object.lookup_code(status),
                     )
    else:
        logging.warning('WITHDRAW: %s %s',
                        status,
                        rest_object.lookup_code(status),
                        )


def setup_logging(default_path='logging.json',
                  default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """Setup logging configuration"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'r') as f:
                config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def update_watcher():
    """Watches for BGP updates from neighbors and triggers RIB change."""
    while True:
        # empty the updates file for Flask application
        open('~/bgp-filter/rib_change/updates.txt', 'w').close()
        setup_logging()
        # listen for BGP updates
        raw_update = sys.stdin.readline().strip()
        try:
            update_json = json.loads(raw_update)
            with open('~/bgp-filter/rib_change/updates.txt', 'a') as f:
                    f.write(raw_update + '\n')
        except ValueError:
            #syslog.syslog(syslog.LOG_ERR, _prefixed('WARNING', e))
            logging.error('Failed JSON conversion for %s',
                          raw_update,
                          exc_info=True)
        else:
            try:
                if update_json['type'] == 'update':
                    render_config(update_json)
            except KeyError:
                logging.error('Failed to find key in %s',
                              raw_update,
                              exc_info=True)
                pass


def tester():
    """Just for testing purposes. Will be removed in official release"""
    with open('/vagrant/BGP-filter/examples/exa-ero.json', 'r') as f:
        setup_logging()
        raw_update = f.read().strip()
        #raw_update = sys.stdin.readline().strip()
        try:
            update_json = json.loads(raw_update)
            #with open('~/bgp-filter/rib_change/updates.txt', 'a') as f:
            #        f.write(raw_update + '\n')
        except ValueError:
            #syslog.syslog(syslog.LOG_ERR, _prefixed('WARNING', e))
            logging.error('Failed JSON conversion for %s',
                          raw_update,
                          exc_info=True)
            pass
        else:
            try:
                if update_json['type'] == 'update':
                    render_config(update_json)
            except KeyError:
                logging.error('Failed to find key in %s',
                              raw_update,
                              exc_info=True)
                pass


if __name__ == "__main__":
    tester()
