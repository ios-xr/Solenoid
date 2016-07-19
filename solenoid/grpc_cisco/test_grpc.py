from cisco_grpc_client import CiscoGRPCClient
import json


def main():
    client = CiscoGRPCClient('192.168.1.2', 57777, 10, 'vagrant', 'vagrant')
    #Test 1: Test Get config json requests
    path = '{"Cisco-IOS-XR-ip-static-cfg:router-static": {"default-vrf": {"address-family": {"vrfipv4": {"vrf-unicast": {"vrf-prefixes": {"vrf-prefix": [null]}}}}}}}'
    path2 = '{"Cisco-IOS-XR-ip-static-cfg:router-static": [null]}'
    result = client.getconfig(path)
    print json.dumps(json.loads(result))
    print ' '
    result2 = client.getconfig(path2)
    print json.dumps(json.loads(result2))
    #Test 2: Test Merge Config
    yangjson = '''
{
    "Cisco-IOS-XR-ip-static-cfg:router-static": {
        "default-vrf": {
            "address-family": {
                "vrfipv4": {
                    "vrf-unicast": {
                        "vrf-prefixes": {
                            "vrf-prefix": [{
                                "prefix": "1.2.3.5",
                                "prefix-length": 32,
                                "vrf-route": {
                                    "vrf-next-hop-table": {
                                        "vrf-next-hop-next-hop-address": [{
                                            "next-hop-address": "10.0.2.2"
                                        }]
                                    }
                                }
                            }, {
                                "prefix": "1.2.3.6",
                                "prefix-length": 32,
                                "vrf-route": {
                                    "vrf-next-hop-table": {
                                        "vrf-next-hop-next-hop-address": [{
                                            "next-hop-address": "10.0.2.2"
                                        }]
                                    }
                                }
                            }, {
                                "prefix": "1.2.3.7",
                                "prefix-length": 32,
                                "vrf-route": {
                                    "vrf-next-hop-table": {
                                        "vrf-next-hop-next-hop-address": [{
                                            "next-hop-address": "10.0.2.2"
                                        }]
                                    }
                                }
                            }, {
                                "prefix": "1.2.3.8",
                                "prefix-length": 32,
                                "vrf-route": {
                                    "vrf-next-hop-table": {
                                        "vrf-next-hop-next-hop-address": [{
                                            "next-hop-address": "10.0.2.2"
                                        }]
                                    }
                                }
                            }, {
                                "prefix": "1.2.3.9",
                                "prefix-length": 32,
                                "vrf-route": {
                                    "vrf-next-hop-table": {
                                        "vrf-next-hop-next-hop-address": [{
                                            "next-hop-address": "10.0.2.2"
                                        }]
                                    }
                                }
                            }]
                        }
                    }
                }
            }
        }
    }
}
'''
    print ' '
    response = client.mergeconfig(yangjson)
    print ' '
    print response.errors
    result2 = client.getconfig(path2)
    print ' '
#    print json.dumps(json.loads(result2))
    print result2
    #Test 3: Test Replace Config
    yangjsonreplace = str(result)
    yangjsondelete = '''
{
    "Cisco-IOS-XR-ip-static-cfg:router-static": {
        "default-vrf": {
            "address-family": {
                "vrfipv4": {
                    "vrf-unicast": {
                        "vrf-prefixes": {
                            "vrf-prefix": [{
                                "prefix": "1.2.3.5",
                                "prefix-length": 32
                            }]
                        }
                    }
                }
            }
        }
    }
}
'''

    errors = client.deleteconfig(yangjsondelete)
    print errors.errors
    result2 = client.getconfig(path2)
    print ' '
#    print json.dumps(json.loads(result2))
    print result2
if __name__ == '__main__':
    main()

