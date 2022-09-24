"""
Updates configuration of a WIFI printer, when the router DHCP might
assign a different IP address to the printer each time it connects to the network
Calls lpinfo -v, to get the IP of a socket printer,
checks if that IP it is the same IP as in /etc/cups/printers.conf
If is not, stops cups daemon, modifies file and restarts cups
It needs sudo, so run crontab with sudo "sudo crontab -e"
and add the command (to run every 5 minutes):
*/5 * * * * python3 <path_to_this_script>/update_wifi_printer.py
"""


from subprocess import run, PIPE
import re
from time import sleep
from typing import Literal

CUPS_CONF_FILE = "/etc/cups/printers.conf"
LPINFO_CMD = "/usr/sbin/lpinfo -v"


def run_shell(command) -> str:
    """Runs command in shell and returns output"""
    return run(command, shell=True, stdout=PIPE).stdout.decode()


def service_cups(what: Literal["start", "stop", "status"]) -> str:
    """Modify runs service cups <what>. E.g. call service_cups("start") for starting cups daemon
    and service_cups("stop") for stopping it. Returns result of the command"""
    return run_shell(f"/usr/sbin/service cups {what}")


if __name__ == '__main__':
    # First, check if cups is up and running
    status = service_cups("status")
    if re.findall("Active: (\w+)", status)[0] != "active":
        print("Cups seems not to be active, starting cups service")
        service_cups("start")

    res = run_shell(LPINFO_CMD)
    print(res)
    match = re.findall("ipp://(.+)", res)
    if not match:
        print("No WIFI printer found")
    else:  # printer found
        new_ip = match[0]
        try:
            with open(CUPS_CONF_FILE, "r") as f:
                printers_conf = f.read()
        except PermissionError:
            print(f"No permission to open {CUPS_CONF_FILE}")
        else:
            ip_printers_conf = re.findall("DeviceURI socket://(.+)", printers_conf)[0]
            if new_ip == ip_printers_conf:
                print("Printer is already correctly configured")
            else:
                printers_conf = printers_conf.replace("DeviceURI socket://{}".format(ip_printers_conf),
                                                      "DeviceURI socket://{}".format(new_ip))
                # Stop cups service
                service_cups("stop")
                # Modify text (it cannot be modified while cups daemon is running)
                with open(CUPS_CONF_FILE, "w") as f:
                    f.write(printers_conf)
                # restart cups service
                service_cups("start")
                print(f"Printer ip modified to {new_ip}")
