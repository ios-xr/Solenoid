##Solenoid-Website
######Author: Karthik Kumaravel

##Description

A Basic website created to show off Solenoid injecting and withdrawing routes that it hears about.
The website has three components, a route filtering component, Exa-bgp announcement table, and a RIB table.
The route filtering component is still under construction and is yet not finished.
The Exa-bgp announcement table, is a table of announcements and withdraws that it learns about from a speaker.
The RIB table is a constant restcall to the RIB table of the IOS-XRv instance. This shows the routes programmed into the RIB table and reflect's Solenoid injections and withdraw.

##Running the website

The website is a simple flask application all you would need to do is cd into the website directory and use python to run the application.

```
cd website
python exabgp_website.py
```  

The website should be up and running. It is currently on the 57780 port. You would need to NAT this port on Vagrant for you to see the website. You can also change which port in the exabgp_website.py file. 
