# Solenoid
### Route Injection Agent

##### Author: Lisa Roach & Karthik Kumaravel
##### Contact: Please use the Issues page to ask questions or open bugs and feature requests. 


## Description:

The end goal of this Route injector app is to be able to take any given logic and
make changes to the prefixes on a RIB table.

The changes to the RIB are accomplished by using [gRPC](http://www.grpc.io/) calls to send JSON modeled by YANG. The YANG model I am currently using is [Cisco-IOS-XR-ip-static-cfg] (https://github.com/YangModels/yang/blob/master/vendor/cisco/xr/600/Cisco-IOS-XR-ip-static-cfg.yang). This model will likely change in the future, see Limitations.

For reading BGP changes I am using [exaBGP] (https://github.com/Exa-Networks/exabgp). Exabgp allows me to monitor BGP network announcements, withdrawals, etc. and trigger the gRPC changes based on these updates. 


#### Current Limitations:

As of now, the IOS-XR 6.0 device I am using does not have completed YANG models
for BGP RIB changes. As a temporary workaround, I can only add static routes
to the RIB.


RESTconf is not available on public images of the IOS-XR 6.X. If you are interested in testing RESTconf, please reach out to your Cisco account team or contact Lisa Roach directly.

### Vagrant:

For an easy Solenoid-in-a-box demonstration, please refer to the [vagrant](https://cto-github.cisco.com/lisroach/Solenoid/tree/master/vagrant) directory. Here you will be able to download a fully functional vagrant environment that has Solenoid up and running already. 

### Usage:

Step 1: Clone this repo and cd into Solenoid.

Step 2: It is highly recommended you install and use a [virtualenv](https://virtualenv.pypa.io/en/stable/).

```
pip install virtualenv

virtualenv venv

source venv/bin/activate
```

Step 3: Install gRPC (if you are using gRPC).

`pip install grpcio`

Step 4: Install Solenoid.

```python setup.py install```

Step 5 : Create a solenoid.config file in your top-level solenoid directory and fill in the values in the key:value pair. Please refer to the Config File section of the wiki for more information.

```
[default]
transport: transport  # Either gRPC or RESTconf
ip: ip_address        # IP address of the destination RIB table
port: port number     # Depends on what is configured for your gRPC or RESTconf servers
username: username    # Username for the router
password: password    # Password for the router
```

Example:

```
[IOS-XRv]
transport: gRPC
ip: 192.168.1.2
port: 57777
username: vagrant
password: vagrant
```

Step 6 (optional): Create a filter.txt file to include the ranges of prefixes to be filtered with. This is a whitelist of prefixes, so all of these will be accepted and all others will be dropped. Single prefixes are also acceptable. Example:

```
1.1.1.0/32-1.1.2.0/32
10.1.1.0/32-10.1.5.0/32
10.1.1.6/32
192.168.1.0/28-192.168.2.0/28
```

Step 7: Set up [exaBGP] (https://github.com/Exa-Networks/exabgp). Form a neighborship with your BGP network.

Step 8: Change your exaBGP configuration file to run the edit_rib.py script. The important part is the process monitor-neighbors section, the rest is basic exaBGP configuration.


Example:

```
group test {
        router-id x.x.x.x;

        process monitor-neighbors {
            encoder json;
            receive {
                parsed;
                updates;
                neighbor-changes;
            }
            run /your/python/location /path/to/solenoid/solenoid/edit_rib.py;
        }

        neighbor y.y.y.y {
            local-address x.x.x.x;
            local as ####;
            peer-as ####;
        }

}

```

If you chose to add a filter file, you must add the path to the file in the run call with the file flag -f (be sure to include the quotes):

```
run /your/python/location /path/to//solenoid/solenoid/edit_rib.py -f '/path/to/filter/file';
```

Step 9: Launch your exaBGP instance. You should see the syslog HTTP status codes if it is successful.

###Testing

In order to run the full suite of unit tests, ensure that grpcio is installed. Run the tests with the following command from the Solenoid/ directory:

```
python -m unittest discover solenoid.tests.mock
```

If you only wish to use RESTconf and will not be testing the gRPC code, feel free to run the following individual tests:

```
python -m unittest solenoid.tests.mock.test_rib

python -m unittest solenoid.tests.mock.test_general
```

To run integration testing, run the following command from the Solenoid/ directory. **CAUTION This will make changes to your router's RIB table! Do not run this code in a production environment!**

For these tests to run, you must provide a properly formatted solenoid.config file, as described in step 3.

```
python -m unittest discover solenoid.tests.integration
```

The following is expected output from the unit tests:

```
python -m unittest discover solenoid.tests.mock
...Tue, 20 Sep 2016 14:50:39 | ERROR    | 20549  | solenoid      | FILTER | invalid IPNetwork 1.1.1.0/43
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 204, in filter_prefixes
    ip1, ip2 = map(IPNetwork, line.split('-'))
  File "/Users/lisroach/Workspace/XRv/Solenoid/venv/lib/python2.7/site-packages/netaddr-0.7.18-py2.7.egg/netaddr/ip/__init__.py", line 933, in __init__
    raise AddrFormatError('invalid IPNetwork %s' % addr)
AddrFormatError: invalid IPNetwork 1.1.1.0/43
..Tue, 20 Sep 2016 14:50:39 | INFO     | 20549  | solenoid      | EOR message
.Tue, 20 Sep 2016 14:50:39 | ERROR    | 20549  | solenoid      | Not a valid update message type
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 154, in render_config
    and 'null' not in update_type['announce']['ipv4 unicast']):
KeyError: 'ipv4 unicast'
.....Tue, 20 Sep 2016 14:50:39 | ERROR    | 20549  | solenoid      | Failed JSON conversion for BGP update
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 233, in update_validator
    json_update = json.loads(raw_update)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/json/__init__.py", line 338, in loads
    return _default_decoder.decode(s)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/json/decoder.py", line 369, in decode
    raise ValueError(errmsg("Extra data", s, end, len(s)))
ValueError: Extra data: line 1 column 531 - line 1 column 534 (char 530 - 533)
.....Tue, 20 Sep 2016 14:50:39 | CRITICAL | 20549  | solenoid      | Something is wrong with your config file: No option 'port' in section: 'default'
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 36, in create_transport_object
    int(config.get(section, 'port')),
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/ConfigParser.py", line 618, in get
    raise NoOptionError(option, section)
NoOptionError: No option 'port' in section: 'default'
.Tue, 20 Sep 2016 14:50:39 | CRITICAL | 20549  | solenoid      | Something is wrong with your config file: File contains no section headers.
file: /Users/lisroach/Workspace/XRv/Solenoid/solenoid/../solenoid.config, line: 1
'transport: GRPC\n'
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 29, in create_transport_object
    config.read(os.path.join(location, '../solenoid.config'))
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/ConfigParser.py", line 305, in read
    self._read(fp, filename)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/ConfigParser.py", line 512, in _read
    raise MissingSectionHeaderError(fpname, lineno, line)
MissingSectionHeaderError: File contains no section headers.
file: /Users/lisroach/Workspace/XRv/Solenoid/solenoid/../solenoid.config, line: 1
'transport: GRPC\n'
.Tue, 20 Sep 2016 14:50:39 | WARNING  | 20549  | solenoid      | Multiple routers not currently supported in the configuration file. Using first router.
.Tue, 20 Sep 2016 14:50:39 | CRITICAL | 20549  | solenoid      | Something is wrong with your config file:
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 45, in create_transport_object
    raise ValueError
ValueError
.Tue, 20 Sep 2016 14:50:39 | INFO     | 20549  | solenoid      | ANNOUNCE | OK
.Tue, 20 Sep 2016 14:50:39 | INFO     | 20549  | solenoid      | WITHDRAW | OK
..Tue, 20 Sep 2016 14:50:39 | CRITICAL | 20549  | solenoid      | Something is wrong with your config file: No option 'port' in section: 'default'
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 36, in create_transport_object
    int(config.get(section, 'port')),
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/ConfigParser.py", line 618, in get
    raise NoOptionError(option, section)
NoOptionError: No option 'port' in section: 'default'
.Tue, 20 Sep 2016 14:50:39 | CRITICAL | 20549  | solenoid      | Something is wrong with your config file: File contains no section headers.
file: /Users/lisroach/Workspace/XRv/Solenoid/solenoid/../solenoid.config, line: 1
'transport: Restconf \n'
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 29, in create_transport_object
    config.read(os.path.join(location, '../solenoid.config'))
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/ConfigParser.py", line 305, in read
    self._read(fp, filename)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/ConfigParser.py", line 512, in _read
    raise MissingSectionHeaderError(fpname, lineno, line)
MissingSectionHeaderError: File contains no section headers.
file: /Users/lisroach/Workspace/XRv/Solenoid/solenoid/../solenoid.config, line: 1
'transport: Restconf \n'
.Tue, 20 Sep 2016 14:50:39 | WARNING  | 20549  | solenoid      | Multiple routers not currently supported in the configuration file. Using first router.
.Tue, 20 Sep 2016 14:50:39 | CRITICAL | 20549  | solenoid      | Something is wrong with your config file:
Traceback (most recent call last):
  File "solenoid/edit_rib.py", line 45, in create_transport_object
    raise ValueError
ValueError
.Tue, 20 Sep 2016 14:50:39 | INFO     | 20549  | solenoid      | ANNOUNCE | OK
.Tue, 20 Sep 2016 14:50:39 | INFO     | 20549  | solenoid      | WITHDRAW | OK
.
----------------------------------------------------------------------
Ran 29 tests in 0.096s

OK
```

If you recieve the final status of 'OK' you are good to go!


