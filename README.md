# Simple script to upgrade cups ip of a wifi printer
When the router DHCP does not provide a fixed IP to the printer,
cups does not look automatically for the new IP and fails to use the printer.

This script looks for the IP of the printer in the network, 
using  `lpinfo -v`,
checks that IP against `/etc/cups/printers.conf`
and in case of change, stops cupsd, modifies the conf file and restarts cupsd.

It needs sudo, so run crontab with `sudo crontab -e`
and add the next line to run command every 5 minutes (only change 5 by the number of required minutes):
```shell
*/5 * * * * python3 <path_to_this_script>/update_wifi_printer.py`
```
