import sys
import os
import ConfigParser
import json
import argparse

from jinja2 import Environment, PackageLoader
from netaddr import IPNetwork, AddrFormatError

from grpc_cisco.grpcClient import CiscoGRPCClient
from grpc_cisco import ems_grpc_pb2
from rest.jsonRestClient import JSONRestCalls
from logs.logger import Logger

_source = 'solenoid'
logger = Logger()


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


def get_status(response):
    """Get the status of the response object.
    :param response: Response object
    :type: depends on the type of transport used
    """
    if isinstance(response, ems_grpc_pb2.ConfigReply):
        return response.errors
    elif isinstance(response, JSONRestCalls):
        return response.content


def rib_announce(rendered_config):
    """Add networks to the RIB table using HTTP PATCH over RESTconf.
    :param rendered_config: Jinja2 rendered configuration file
    :type rendered_config: unicode
    """
    transport_object = create_transport_object()
    response = transport_object.patch(rendered_config)
    status = get_status(response)
    if status == '':
        logger.info('ANNOUNCE | {code} '.format(
            code='OK'
            ),
            _source
        )
    else:
        logger.warning('ANNOUNCE | {code} | {reason}'.format(
            code='FAIL',
            reason=status
            ),
            _source
        )


def rib_withdraw(withdrawn_prefixes):
    """Remove the withdrawn prefix from the RIB table.
        :param new_config: The prefix and prefix-length to be removed
        :type new_config: str
    """
    transport_object = create_transport_object()
    # Delete each prefix one at a time.
    for withdrawn_prefix in withdrawn_prefixes:
        if isinstance(transport_object, CiscoGRPCClient):
            url = '{{"Cisco-IOS-XR-ip-static-cfg:router-static": {{"default-vrf": {{"address-family": {{"vrfipv4": {{"vrf-unicast": {{"vrf-prefixes": {{"vrf-prefix": [{{"prefix": "{bgp_prefix}","prefix-length": {prefix_length}}}]}}}}}}}}}}}}}}'
        else:  # Right now there is only gRPC and RESTconf, more elif will be required w/ more options
            url = 'Cisco-IOS-XR-ip-static-cfg:router-static/default-vrf/address-family/vrfipv4/vrf-unicast/vrf-prefixes/vrf-prefix={bgp-prefix},{prefix-length}'
        bgp_prefix, prefix_length = withdrawn_prefix.split('/')
        url = url.format(bgp_prefix=bgp_prefix, prefix_length=prefix_length)
        response = transport_object.delete(url)
        status = get_status(response)
        if status == '':
            logger.info('WITHDRAW | {code}'.format(
                code='OK'
                ),
                _source
            )
        else:
            logger.warning('WITHDRAW | {code} | {reason}'.format(
                code='FAIL',
                reason=status
                ),
                _source
            )


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
                env = Environment(loader=PackageLoader('solenoid',
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


def filter_prefixes(prefixes):
    """Filters out prefixes that do not fall in ranges indicated in filter.txt

    :param prefixes: List of prefixes bgpBGP announced or withdrew
    :type prefixes: list of strings

    """
    # TODO: Add the capability of only have 1 IP, not a range.
    print 'in filter_prefixes'
    with open(filepath) as filterf:
        final = []
        try:
            prefixes = map(IPNetwork, prefixes)
            for line in filterf:
                if '-' in line:
                    # Convert it all to IPNetwork for comparison.
                    ip1, ip2 = map(IPNetwork, line.split('-'))
                    final += [str(prefix) for prefix in prefixes if ip1 <= prefix <= ip2]
                    print final
                else:
                    ip = IPNetwork(line)
                    final += [str(ip)]
                    print final
            return final
        except AddrFormatError, e:
            print e
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
