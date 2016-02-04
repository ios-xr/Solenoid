"""
This module calls a RESTconf GET request on the server identified.
The GET request option is defined by the user in the CLI during the call.
You can specify multiple GET calls as once, or list all the options.

Examples:
    $ python REST_GET.py bgp
    $ python REST_GET.py bgp isis cisco_bgp
    $ python REST_GET.py options

 """

import requests
import sys
from requests.auth import HTTPBasicAuth
import getpass


def get_choice(choice):
    '''Define which GET is called'''
    options = {
        'oc_bgp': 'bgp:bgp',
        'cisco_ldp': 'Cisco-IOS-XR-mpls-ldp-cfg:mpls-ldp',
        'cisco_isis': 'Cisco-IOS-XR-clns-isis-cfg:isis',
        'run': '',
        'oc_bgp_neigh': 'bgp:bgp/neighbors',
        'cisco_bgp': 'Cisco-IOS-XR-ipv4-bgp-cfg:bgp',
        'cisco_bgp_global': 'Cisco-IOS-XR-ipv4-bgp-cfg:bgp/instance/instance-as/four-byte-as/default-vrf/global',
        'cisco_bgp_neigh': 'Cisco-IOS-XR-ipv4-bgp-cfg:bgp/instance/instance-as/four-byte-as/default-vrf/global',
        'cisco_bgp_neigh_as': 'Cisco-IOS-XR-ipv4-bgp-cfg:bgp/instance/instance-as/four-byte-as/default-vrf/bgp-entity/neighbors/neighbor/remote-as',
        'cisco_bgp_neigh_desc': 'Cisco-IOS-XR-ipv4-bgp-cfg:bgp/instance/instance-as/four-byte-as/default-vrf/bgp-entity/neighbors/neighbor/description',
        'cisco_bgp_neigh_address_RPL': 'Cisco-IOS-XR-ipv4-bgp-cfg:bgp/instance/instance-as/four-byte-as/default-vrf/bgp-entity/neighbors/neighbor/neighbor-afs',
        'cisco_static': 'Cisco-IOS-XR-ip-static-cfg:router-static',
        'cisco_isis': 'Cisco-IOS-XR-clns-isis-cfg:isis',
        'cisco_isis_address': 'Cisco-IOS-XR-clns-isis-cfg:isis/instances/instance/afs',
        'cisco_isis_int': 'Cisco-IOS-XR-clns-isis-cfg:isis/instances/instance/interfaces',
        'cisco_isis_int_address': 'Cisco-IOS-XR-clns-isis-cfg:isis/instances/instance/interfaces/interface/interface-afs',
        'cisco_interfaces': 'Cisco-IOS-XR-ifmgr-cfg:interface-configurations',
        'cisco_rpl': 'Cisco-IOS-XR-policy-repository-cfg:routing-policy',
        'cisco_mpls_ldp': 'Cisco-IOS-XR-mpls-ldp-cfg:mpls-ldp'
    }
    if choice != "options":
        return options.get(choice, "error")
    else:
        return options


def rest_get():
    '''Complete a REST GET request based on the cli arguments'''
    myheaders = ({'Accept': 'application/yang.data+json, application/yang.errors+json'})
    for arg in sys.argv[1:]:
        my_var = get_choice(arg)
        if type(my_var) is str:
            if my_var != 'error':
                username = raw_input("Username: ")
                password = getpass.getpass("Password: ")
                #Change to your own IP address and port
                response = (requests.get("http://<ip address:port>/restconf/data/{}?content=config".format(
                                         my_var),
                                         headers=myheaders,
                                         auth=HTTPBasicAuth(username,
                                                            password)
                                         )
                            )
                print response.content
            else:
                print "Your argument could not be found. To see your options use 'python REST_GET.py options'"
        else:
            for item in my_var:
                print item
