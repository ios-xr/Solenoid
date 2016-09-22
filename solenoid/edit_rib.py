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

SOURCE = 'solenoid'
LOGGER = Logger()


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
                LOGGER.warning('Multiple routers not currently supported in the configuration file. Using first router.', SOURCE)
            section = config.sections()[0]
            arguments = (
                config.get(section, 'ip'),
                int(config.get(section, 'port')),
                config.get(section, 'username'),
                config.get(section, 'password')
                )
            if config.get(section, 'transport').lower() == 'grpc':
                return CiscoGRPCClient(*arguments)
            if config.get(section, 'transport').lower() == 'restconf':
                return JSONRestCalls(*arguments)
        else:
            raise ValueError
    except (ConfigParser.Error, ValueError), e:
        LOGGER.critical(
            'Something is wrong with your config file: {}'.format(
                e.message
            ),
            SOURCE
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


def rib_announce(rendered_config, transport):
    """Add networks to the RIB table using HTTP PATCH over RESTconf.
    :param rendered_config: Jinja2 rendered configuration file
    :type rendered_config: unicode
    """
    response = transport.patch(rendered_config)
    status = get_status(response)
    if status == '' or status is None:
        LOGGER.info('ANNOUNCE | {code} '.format(
            code='OK'
            ),
            SOURCE
        )
    else:
        LOGGER.warning('ANNOUNCE | {code} | {reason}'.format(
            code='FAIL',
            reason=status
            ),
            SOURCE
        )


def rib_withdraw(withdrawn_prefixes, transport):
    """Remove the withdrawn prefix from the RIB table.
        :param new_config: The prefix and prefix-length to be removed
        :type new_config: str
    """
    # Delete the prefixes in bulk with gRPC.
    if isinstance(transport, CiscoGRPCClient):
        url = '{{"Cisco-IOS-XR-ip-static-cfg:router-static": {{"default-vrf": {{"address-family": {{"vrfipv4": {{"vrf-unicast": {{"vrf-prefixes": {{"vrf-prefix": [{withdraw}]}}}}}}}}}}}}}}'
        prefix_info = '{{"prefix": "{bgp_prefix}","prefix-length": {prefix_length}}}'
        prefix_list = []
        for withdrawn_prefix in withdrawn_prefixes:
            bgp_prefix, prefix_length = withdrawn_prefix.split('/')
            prefix_list += [
            prefix_info.format(
                bgp_prefix=bgp_prefix,
                prefix_length=prefix_length
                )
            ]
            prefix_str = ', '.join(prefix_list)
        url = url.format(withdraw=prefix_str)
        response = transport.delete(url)
        status = get_status(response)
    else:  # Right now there is only gRPC and RESTconf, more elif will be required w/ more options.
    # Delete the prefixes one at a time with RESTconf.
        for withdrawn_prefix in withdrawn_prefixes:
            url = 'Cisco-IOS-XR-ip-static-cfg:router-static/default-vrf/address-family/vrfipv4/vrf-unicast/vrf-prefixes/vrf-prefix={bgp_prefix},{prefix_length}'
            bgp_prefix, prefix_length = withdrawn_prefix.split('/')
            url = url.format(
                bgp_prefix=bgp_prefix,
                prefix_length=prefix_length
            )
            response = transport.delete(url)
            status = get_status(response)
    if status is None or status == '':
        LOGGER.info('WITHDRAW | {code}'.format(
            code='OK'
            ),
            SOURCE
        )
    else:
        LOGGER.warning('WITHDRAW | {code} | {reason}'.format(
            code='FAIL',
            reason=status
            ),
            SOURCE
        )

def render_config(json_update, transport):
    """Take a BGP command and translate it into yang formatted JSON
    :param json_update: JSON dictionary
    :type json_update: dict
    """
    # Check if any filtering has been applied to the prefixes.
    try:
        filt = bool(FILEPATH is not None and os.path.getsize(FILEPATH) > 0)
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
                if len(prefixes) > 0:
                    env = Environment(loader=PackageLoader('solenoid',
                                                           'templates')
                                     )
                    env.filters['to_json'] = json.dumps
                    template = env.get_template('static.json')
                    # Render the template and make the announcement.
                    rib_announce(template.render(next_hop=next_hop,
                                                 prefixes=prefixes),
                                transport
                                )
                else:
                    return
            elif 'withdraw' in update_type:
                bgp_prefixes = update_type['withdraw']['ipv4 unicast'].keys()
                # Filter the prefixes if needed.
                if filt:
                    bgp_prefixes = filter_prefixes(bgp_prefixes)
                if len(bgp_prefixes) > 0:
                    rib_withdraw(bgp_prefixes, transport)
                else:
                    return
        else:
            LOGGER.info('EOR message', SOURCE)
    except KeyError:
        LOGGER.error('Not a valid update message type', SOURCE)
        raise


def filter_prefixes(prefixes):
    """Filters out prefixes that do not fall in ranges indicated in filter.txt

    :param prefixes: List of prefixes bgpBGP announced or withdrew
    :type prefixes: list of strings

    """
    with open(FILEPATH) as filterf:
        final = []
        try:
            prefixes = map(IPNetwork, prefixes)
            for line in filterf:
                if '-' in line:
                    # Convert it all to IPNetwork for comparison.
                    ip1, ip2 = map(IPNetwork, line.split('-'))
                    final += [str(prefix) for prefix in prefixes if ip1 <= prefix <= ip2]
                else:
                    ip = IPNetwork(line)
                    final += [str(prefix) for prefix in prefixes if prefix == ip]
            return final
        except AddrFormatError, e:
            LOGGER.error('FILTER | {}'.format(e), SOURCE)
            raise


def update_file(raw_update):
    """Update the updates.txt file with the newest exaBGP JSON string.
        :param raw_update: The JSON string from exaBGP
        :type raw_update: str
    """
    # Add the change to the update file.
    here = os.path.dirname(os.path.realpath(__file__))
    updates_filepath = os.path.join(here, 'updates.txt')
    with open(updates_filepath, 'a') as f:
        f.write(str(raw_update) + '\n')


def update_validator(raw_update, transport):
    """Translate update to JSON and send it to be rendered.
        :param raw_update: Raw exaBGP message.
        :type raw_update: JSON
    """
    try:
        json_update = json.loads(raw_update)
        # If it is an update, make the RIB changes.
        if json_update['type'] == 'update':
            render_config(json_update, transport)
            # Add the update to a file to keep track.
            update_file(raw_update)
    except ValueError:
        LOGGER.error('Failed JSON conversion for BGP update', SOURCE)
        raise
    except KeyError:
        LOGGER.debug('Not a valid update message type', SOURCE)
        raise


def update_watcher():
    """Watches for BGP updates and triggers a RIB change when update is heard."""
    # Continuously listen for updates.
    transport = create_transport_object()
    while 1:
        raw_update = sys.stdin.readline().strip()
        update_validator(raw_update, transport)

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-f', type=str)
    ARGS = PARSER.parse_args()
    global FILEPATH
    FILEPATH = ARGS.f
    update_watcher()
