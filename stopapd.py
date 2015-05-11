import subprocess
import time
import os

while True:
	file=open('/home/pi/orbmi/test123.txt')
	length=len(file.readline())
	file.close()

	if length>0:
		print "set_wifi ran!"
		file=open('/home/pi/orbmi/test123.txt','w')
		file.close()
		
		subprocess.call("sudo service hostapd stop", shell= True)
		subprocess.call("sudo service isc-dhcp-server stop", shell = True)
		subprocess.call("sudo ifdown wlan0", shell=True)
		subprocess.call("sudo /etc/init.d/networking stop",shell=True)
		subprocess.call("cp /etc/network/interfaces-manual /etc/network/interfaces", shell=True)
		subprocess.call("sudo /etc/init.d/networking start",shell=True)
		subprocess.call("sudo ifup wlan0", shell=True)
		print "end of stopapd"		
#subprocess.call("sudo reboot", shell=True)
