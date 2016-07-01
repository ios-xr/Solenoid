import json
import sys
import os
import ConfigParser
import argparse

from netaddr import IPNetwork, AddrFormatError
from jinja2 import Environment, PackageLoader
from rest.jsonRestClient import JSONRestCalls
from logs.logger import Logger

_source = 'solenoid'
logger = Logger()


def render_config(json_update):
    """Take a BGP command and translate it into yang formatted JSON

    :param json_update: JSON dictionary
    :type json_update: dict

    """
    # Check if any filtering has been applied to the prefixes.
    try:
        if filepath is not None and os.path.getsize(filepath) > 0:
            filt = True
        else:
            filt = False
    except OSError:
        filt = False

    # Render the config.
    try:
        update_type = json_update['neighbor']['message']
        if 'eor' not in update_type:
            update_type = json_update['neighbor']['message']['update']
            # Check if it is an announcement or withdrawal.
            if ('announce' in update_type
                and 'null' not in update_type['announce']['ipv4 unicast']):
                updated_prefixes = update_type['announce']['ipv4 unicast']
                next_hop = updated_prefixes.keys()[0]
                prefixes = updated_prefixes.values()[0].keys()
                if filt:
                    prefixes = filter_prefixes(prefixes)
                # Set env variable for Jinja2.
                env = Environment(loader=PackageLoader('edit_rib',
                                                       'templates')
                                  )
                env.filters['to_json'] = json.dumps
                template = env.get_template('static.json')
                # Render the template and make the announcement.
                rib_announce(template.render(next_hop=next_hop,
                                             prefixes=prefixes)
                             )
            elif 'withdraw' in update_type:
                bgp_prefixes = update_type['withdraw']['ipv4 unicast'].keys()
                # Filter the prefixes if needed.
                if filt:
                    bgp_prefixes = filter_prefixes(bgp_prefixes)
                rib_withdraw(bgp_prefixes)
        else:
            logger.info('EOR message', _source)
    except KeyError:
        logger.error('Not a valid update message type', _source)


def create_rest_object():
    """Create a restCalls object.
        Reads in a file containing username, password, and
        ip address:port, in that order.

        This method could be eliminated and the restCalls(username, password,
        ip_address:port) replace all calls to create_rest_object().
        This method exists in order to separate passwords from github.

        :returns: restCalls object
        :rtype: restCalls class object
    """
    location = os.path.dirname(os.path.realpath(__file__))
    try:
        config = ConfigParser.ConfigParser()
        try:
            config.read(os.path.join(location, '../solenoid.config'))
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


def rib_announce(rendered_config):
    """Add networks to the RIB table using HTTP PATCH over RESTconf.

    :param rendered_config: Jinja2 rendered configuration file
    :type rendered_config: unicode

    """
    rest_object = create_rest_object()
    response = rest_object.patch(
        'Cisco-IOS-XR-ip-static-cfg:router-static',
        rendered_config
    )
    status = response.status_code
    if status in xrange(200, 300):
        logger.info('ANNOUNCE | {code} | {reason}'.format(
            code=status,
            reason=response.reason
            ),
            _source
        )
    else:
        logger.warning('ANNOUNCE | {code} | {reason}'.format(
            code=status,
            reason=response.reason
            ),
            _source
        )


def rib_withdraw(withdrawn_prefixes):
    """Remove the withdrawn prefix from the RIB table.

        :param new_config: The prefix and prefix-length to be removed
        :type new_config: str
    """
    rest_object = create_rest_object()
    # Delete each prefix one at a time.
    for withdrawn_prefix in withdrawn_prefixes:
        url = 'Cisco-IOS-XR-ip-static-cfg:router-static/default-vrf/address-family/vrfipv4/vrf-unicast/vrf-prefixes/vrf-prefix={},{}'
        bgp_prefix, prefix_length = withdrawn_prefix.split('/')
        url = url.format(bgp_prefix, prefix_length)
        response = rest_object.delete(url)
        status = response.status_code
        if status in xrange(200, 300):
            logger.info('WITHDRAW | {code} | {reason}'.format(
                code=status,
                reason=response.reason
                ),
                _source
            )
        else:
            logger.warning('WITHDRAW | {code} | {reason}'.format(
                code=status,
                reason=response.reason
                ),
                _source
            )


def filter_prefixes(prefixes):
    """Filters out prefixes that do not fall in ranges indicated in filter.txt

    :param prefixes: List of prefixes bgpBGP announced or withdrew
    :type prefixes: list of strings

    """
    # TODO: Add the capability of only have 1 IP, not a range.
    with open(filepath) as filterf:
        final = []
        try:
            for line in filterf:
                    # Convert it all to IPNetwork for comparison.
                    ip1, ip2 = map(IPNetwork, line.split('-'))
                    prefixes = map(IPNetwork, prefixes)
                    final += [str(prefix) for prefix in prefixes if ip1 <= prefix <= ip2]
            return final
        except AddrFormatError, e:
            logger.error('FILTER | {}'.format(e), _source)


def update_file(raw_update):
    # Add the change to the update file.
    here = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(here, 'updates.txt')
    with open(filepath, 'a') as f:
        f.write(str(raw_update) + '\n')


def update_validator(raw_update):
    """Translate update to JSON and send it to be rendered.

        :param raw_update: Raw exaBGP message.
        :type raw_update: JSON

    """
    try:
        json_update = json.loads(raw_update)
        # If it is an update, make the RIB changes.
        if json_update['type'] == 'update':
            render_config(json_update)
            # Add the update to a file to keep track.
            update_file(raw_update)
    except ValueError:
        logger.error('Failed JSON conversion for BGP update', _source)
    except KeyError:
        logger.debug('Not a valid update message type', _source)


def update_watcher():
    """Watches for BGP updates and triggers a RIB change when update is heard."""
    # Continuously listen for updates.
    while 1:
        raw_update = sys.stdin.readline().strip()
        update_validator(raw_update)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str)
    args = parser.parse_args()
    global filepath
    filepath = args.f
    update_watcher()
