#
# wireguard2mikrotik
#
This is a connector that synchronises Wireguard configuration file with Mikrotik router via REST API. It is useful if you do not want to manage Wireguard clients in the Mikrotik interface. It is basically designed for wireguard-ui but works with any program that manipulates wg0.conf file. 
  
Install:  
curl -sSL https://github.com/g-boruzs/wireguard2mikrotik/raw/main/install.sh | bash  
  
  
usage: wireguardui-mikrotik.py [-h] [-d]  

    
Applying wireguard-ui configuration on RouterOS.
Before first use, configure the variables.
  
optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Enable debug mode.  
   
