import argparse
import configparser
import json
import shutil
import urllib3
from requests.auth import HTTPBasicAuth
import requests

urllib3.disable_warnings()

# Configuration
router = 'router.example.com'
apiURL = 'http://'+router+'/rest'  # Please enter your IP address
apiUsername = 'admin'  # Input your username here
apiPassword = '*****'  # Input your password here
origconfigfile = '/etc/wireguard/wg0.conf'
preparedconfigfile = '/tmp/wg0.conf'
routerosinterface = 'wg0'


# Defining global variables
wguiconf = []  # Wireguard-UI configuration as list of dicts
rosconf = []  # RouterOS configuration as list of dicts

def get_router_peers():
    if args.debug:
        print('\033[32m' + "### Getting peers from the router. ###" + '\033[0m')
    response = requests.get(apiURL+'/interface/wireguard/peers', auth=HTTPBasicAuth(apiUsername, apiPassword), verify=False)
    if args.debug:
        print('\033[32m' + "Router config in json:" + '\033[0m')
        print(response.json())
    for peer in response.json():
        rosconf.append({'publickey': peer["public-key"], 'allowedips': peer["allowed-address"], 'interface': peer["interface"], 'comment': peer["comment"], 'id': peer[".id"]})
    if args.debug:
        print('\033[32m' + "Router config translated using common variable names:" + '\033[0m')
        print(rosconf)

def get_router_interface_name():
    response = requests.get(apiURL+'/interface/wireguard', auth=HTTPBasicAuth(apiUsername, apiPassword), verify=False)
    for wgint in response.json():
        routerosinterface = wgint["name"]
    if args.debug:
        print('\033[32m' + "Getting router interface name: " + '\033[0m' + routerosinterface)

def prepare_config_file(origconfigfile): # Configparser cannot work with sections with same name so I add numbers to the ends.
    if args.debug:
        print('\033[32m' + "Prepare config file (numbering): " + '\033[0m' + origconfigfile + '\033[32m' + "->" + '\033[0m' + preparedconfigfile)
    with open(origconfigfile, 'r') as file:
        section_number = 1
        output_lines = []
        for line in file:
            line = line.strip()
            if line.startswith("[Peer]"):
                output_lines.append(f"[Peer {section_number}]")
                section_number += 1
            else:
                output_lines.append(line)
    with open(preparedconfigfile, 'w') as file:
        file.write("\n".join(output_lines))

def parse_config_file(preparedconfigfile): # Getting peers from wirreguard config file.
    if args.debug:
        print('\033[32m' + "Parsing prepared wireguard-ui config file: " + '\033[0m' + preparedconfigfile)
    config = configparser.ConfigParser()
    config.read(preparedconfigfile)
    if config.has_section("Interface"):
        if args.debug:
            print('\033[32m' + "Remove interface section from wireguard-ui config file: " + '\033[0m' + preparedconfigfile)
        config.remove_section("Interface")
    for section in config.sections():
        peer_data = {}
        for key, value in config.items(section):
            peer_data[key] = value
        wguiconf.append(peer_data)
    if args.debug:
        print('\033[32m' + "Config parsed to json: " + '\033[0m' + preparedconfigfile)
        print(wguiconf)

def add_new():
    if args.debug:
        print('\033[32m' + "### Adding new peers to router. ###" + '\033[0m')
        print('\033[32m' + "Router config:" + '\033[0m')
        print(rosconf)
        print('\033[32m' + "Wireguard-ui config:" + '\033[0m')
        print(wguiconf)
    missing_elements = [element for element in wguiconf if element['publickey'] not in [r['publickey'] for r in rosconf]]
    if args.debug:
        print('\033[32m' + "Elements missing from router:" + '\033[0m')
        print(missing_elements)
    for newpeer in missing_elements:
        if args.debug:
            print('\033[32m' + "Adding peer:" + '\033[0m')
            print(newpeer['publickey'])
        response = requests.put(apiURL+'/interface/wireguard/peers', auth=HTTPBasicAuth(apiUsername, apiPassword), verify=False, data=json.dumps({"public-key": newpeer['publickey'], "interface": routerosinterface, "allowed-address": newpeer['allowedips'], "preshared-key": newpeer['presharedkey'], "comment": "Managed by Wireguard-UI"}))

def remove_deleted():
    if args.debug:
        print('\033[32m' + "### Remove deleted peers. ###" + '\033[0m')
    missing_elements = [element for element in rosconf if element['publickey'] not in [r['publickey'] for r in wguiconf]]
    if args.debug:
        print('\033[32m' + "Elements missing from wireguard-ui:" + '\033[0m')
        print(missing_elements)
    for peer in missing_elements:
        if peer['comment'] == "Managed by Wireguard-UI":
            id = peer['id']
            if args.debug:
                print('\033[32m' + "Deleting peer from router: " + '\033[0m' + id)
            response = requests.delete(apiURL+'/interface/wireguard/peers/'+id, auth=HTTPBasicAuth(apiUsername, apiPassword), verify=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Applying wireguard-ui configuration on RouterOS.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")
    args = parser.parse_args()
    get_router_peers()
    get_router_interface_name()
    prepare_config_file(origconfigfile)
    parse_config_file(preparedconfigfile) 
    add_new()
    remove_deleted()
