import json
import sys
import os
from jinja2 import Environment, PackageLoader
#sys.path.append('/home/cisco/exabgp/bgp-filter/')
from rest.jsonRestClass import JSONRestCalls
from logs.logger import Logger


_source = 'bgp-filter'
logger = Logger()


def render_config(update_json):
    """Take a exa command and translate it into yang formatted JSON

    :param update_json: The exa bgp string that is sent to stdout
    :type update_json: str

    """
    # check if any filtering has been applied to the prefixes
    try:
        if os.path.getsize('/vagr3ant/bgp-filter/rib_change/filter.txt') > 0:
            filt = True
    except OSError:
        filt = False
        pass

    # render the config
    try:
        update_type = update_json['neighbor']['message']['update']
        if 'announce' in update_type:
            updated_prefixes = update_type['announce']['ipv4 unicast']
            prefixes = updated_prefixes.values()[0]
            next_hop = updated_prefixes.keys()[0]
            # Filter the prefixes
            if filt:
                prefixes = filter_prefixes(prefixes)
            # set env variable for jinja2
            env = Environment(loader=PackageLoader('rib_change',
                              'templates'))
            env.filters['to_json'] = json.dumps
            template = env.get_template('static.json')
            rib_announce(template.render(next_hop=next_hop,
                                         prefixes=prefixes))
        elif 'withdraw' in update_type:
            exa_prefixes = update_type['withdraw']['ipv4 unicast'].keys()
            # Filter the prefixes
            if filt:
                exa_prefixes = filter_prefixes(prefixes)
            for withdrawn_prefix in exa_prefixes:
                rib_withdraw(withdrawn_prefix)
    except ValueError:  # If we hit an eor or other type of update
        logger.warning('Failed JSON conversion for exa update',
                       _source
                       )


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
    with open('/vagrant/bgp-filter/rib_change/edit_rib.config', 'r') as f:
        lines = f.readlines()
    return JSONRestCalls(lines[0].replace("\r\n", ""),
                         lines[1].replace("\r\n", ""),
                         lines[2].replace("\r\n", ""),
                         lines[3].replace("\r\n", "")
                         )


def rib_announce(rendered_config):
        """Add networks to the RIB table using HTTP PATCH over RESTconf.

        :param rendered_config: Jinja2 rendered configuration file
        :type rendered_config: unicode

        """
        rest_object = create_rest_object()
        response = rest_object.patch(
            rendered_config,
            'Cisco-IOS-XR-ip-static-cfg:router-static'
            )
        status = response.status_code
        if status >= 200 and status < 300:  # Status code is good
            logger.info('ANNOUNCE | {code} | {type}'.format(
                code=status,
                type=rest_object.lookup_code(status)
                ),
                _source
            )
        else:
            logger.warning('ANNOUNCE | {code} | {type}'.format(
                code=status,
                type=rest_object.lookup_code(status)
                ),
                _source
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
        logger.info('WITHDRAW | {code} | {type}'.format(
            code=status,
            type=rest_object.lookup_code(status)
            ),
            _source
        )
    else:
        logger.warning('WITHDRAW | {code} | {type}'.format(
            code=status,
            type=rest_object.lookup_code(status)
            ),
            _source
        )


def filter_prefixes(prefixes):
    for values in prefixes:
        print values


def update_watcher():
    """Watches for BGP updates from neighbors and triggers RIB change."""
    open('~/bgp-filter/rib_change/updates.txt', 'w').close()
    logger = Logger()
    while True:
        # listen for BGP updates
        raw_update = sys.stdin.readline().strip()
        try:
            update_json = json.loads(raw_update)
            with open('~/bgp-filter/rib_change/updates.txt', 'a') as f:
                    f.write(raw_update + '\n')
        except ValueError:
            logger.error('Failed JSON conversion for exa update',
                         _source
                         )
        else:
            try:
                if update_json['type'] == 'update':
                    render_config(update_json)
            except KeyError:
                logger.warning('Failed to find "update" keyword in exa update',
                               'bgp-filter'
                               )
                pass


def tester():
    """Just for testing purposes. Will be removed in official release"""
    #open('~/bgp-filter/rib_change/updates.txt', 'w').close()
    logger = Logger()
    with open('/vagrant/bgp-filter/examples/exa-announce.json', 'r') as f:
        raw_update = f.read().strip()
        #raw_update = sys.stdin.readline().strip()
        try:
            update_json = json.loads(raw_update)
            #with open('~/bgp-filter/rib_change/updates.txt', 'a') as f:
            #        f.write(raw_update + '\n')
        except ValueError:
            logger.error('Failed JSON conversion for exa update',
                         _source
                         )
        else:
            try:
                if update_json['type'] == 'update':
                    # if everything is right, render the config
                    render_config(update_json)
            except KeyError:
                logger.error('Failed to find "update" keyword in exa update',
                             'bgp-filter'
                             )


if __name__ == "__main__":
    tester()
