#
# wireguard2mikrotik
#
This is a connector that synchronises Wireguard configuration file with Mikrotik router via REST API. It is useful if you do not want to manage Wireguard clients in Mikrotik Winbox. It is basically designed for wireguard-ui but works with any program that manipulates wg0.conf file.

Mechanism:
It's monitoring /etc/wireguard/wg0.conf file and compares it with the router's configuration when the fie changes.
The base key of the comparison is the private key.
If it finds a peer that exists on routerboard but doesn't in wg0.conf then it deletes that peer from the routerboard.
If it finds a peer that exists in wg0.cone but doesn't on routerboard then it creates the peer on routerboard.
It adds "Managed by Wireguard-UI" comment to all peers on routeros and manipulates only the peers that have this comment.
  
Installation as a systemd service:  
curl -sSL https://github.com/g-boruzs/wireguard2mikrotik/raw/main/install.sh | bash  
After the installation configure the variables in /opt/wireguard2mikrotik/wireguardui-mikrotik.py
  
Manual usage: 
Just download wireguardui-mikrotik.py and use it as you want.
wireguardui-mikrotik.py [-h] [-d]  
  
optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Enable debug mode.  
   
