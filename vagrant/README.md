# Solenoid-Vagrant
#####Vagrant for Solenoid application demo
#####Author: Karthik Kumaravel
##### Contact: Please use the Issues page to ask questions or open bugs and feature requests.

### Overview
This is a Vagrant box set up to demo the Solenoid application. This Vagrant uses two virtualbox VMs, a IOS-XRv image and an ubuntu trusty image. The plumbiing and demo functions are brough up through bash scripts to allow you to with the Solenoid application without hassle, and demo it to others.

### Set Up

To install the application.

Step 1. Set up Virtualbox and Vagrant on your device <br />
Step 2. Clone this repo <br />
Step 3. Request access to the base box for IOS-XRv, using the link bellow<br />
https://xrdocs.github.io/getting-started/steps-download-iosxr-vagrant <br />
Step 3. Download the IOS-XRv vagrant box through the following link, and follow the instructions to add the base box.<br />
https://xrdocs.github.io/application-hosting/tutorials/iosxr-vagrant-quickstart
https://xrdocs.github.io/getting-started/steps-download-iosxr-vagrant <br />
Step 4. Download release tarball and add it the directory /vagrant/xrv/. This is the container image that will sit on the IOS-XRv vm<br />
Step 5. In a terminal screen change directory into the vagrant directory of the repository. The vagrant file is located here.<br />
Step 6. ```vagrant up``` <br />

This is all you need to get the repo working with all the configs in place for the demo.

### Navigating the Vagrant environment

This Vagrant environment has 5 components to it, XR bash, XR cli, Solenoid, and Exabgp. Solenoid runs on an Ubuntu lxc container running on IOS-XRv<br />
This is how to access each of these components.

####XR bash
From the vagrant folder
```vagrant ssh xrv``` <br />
XR CLI and Solenoid is accessed in from XR bash
######XR CLI
From XR Bash
```ssh 10.1.1.5``` <br />
password: vagrant
######Solenoid
From XR Bash
```ssh cisco@192.168.1.2``` <br />
password: cisco
####ExaBGP is running in a Ubuntu VM
From the vagrant folder
```vagrant ssh ubuntu``` <br />
######Exabgp is running in a screen
```sudo screen -r``` <br />
note: This will be changed to not use sudo.

### How to use this demo.
There is a website to use for demo purposes to show the application running. localhost:57780 is the address of the website.

