# BGP-filter
##### Author: Lisa Roach
##### Email: lisroach@cisco.com

## Description:

The end goal of this BGP-filter app is to be able to take any given logic and 
make changes to the prefixes on a RIB table.

The changes to the RIB are accomplished by using RESTconf calls to send JSON modeled by YANG. The YANG model I am currently using is [Cisco-IOS-XR-ip-static-cfg] (https://github.com/YangModels/yang/blob/master/vendor/cisco/xr/600/Cisco-IOS-XR-ip-static-cfg.yang). This model will likely change in the future, see Limitations.

For reading BGP changes I am using [exaBGP] (https://github.com/Exa-Networks/exabgp). Exabgp allows me to monitor BGP network announcements, withdrawals, etc. and trigger the RESTconf changes based on these updates. 

### Work in Progress:

Be able to update RIB only with networks from preferred neighbors (based on some blackbox of logic)

Create tar of project including exaBGP and GUI interface for exaBGP (gui be based on the [ERCO](https://erco.xyz/) project).


#### Current Limitations:

As of now, the IOS-XR 6.0 device I am using does not have completed YANG models
for BGP RIB changes. As a temporary workaround, I can only add static routes
to the RIB.


### Usage:

Step 1: Set up [exaBGP] (https://github.com/Exa-Networks/exabgp). Form a neighborship with your BGP network. 

Step 2: Make sure RESTconf calls are working from your device to the RIB table

Example test (you should recieve your device's whole configuration):

'''
curl -X GET -H "Accept:application/yang.data+json,application/yang.errors+json" -H "Authorization: <INSERT YOUR AUTH CODE>" http://<YOUR IP>/restconf/data/?content=config
'''


Step 2: Clone this project onto your device

Step 3: Change your exaBGP configuration file to run the edit_rib.py script. 

Example:

'''
group test {
        router-id x.x.x.x;

        process monitor-neighbors {
            encoder json;
            receive {
                parsed;
                updates;
                neighbor-changes;
            }
            run /your/python/location /path/to/bgp-filter/rest_calls/edit_rib.py;
        }

        neighbor y.y.y.y {
            local-address x.x.x.x;
            local as ####;
            peer-as ####;
        }

}

'''

Step 4: Launch your exaBGP instance. You should see the syslog HTTP status codes if it is successful. 
