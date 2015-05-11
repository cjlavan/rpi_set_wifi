import subprocess
import time
import os


f=open('/sys/class/net/wlan0/address')
MACADD = f.readline()
f.close()


MACSTR = MACADD.replace(":","")
print MACSTR

str1 = "ssid=orbmi_"
str2 = str1+MACSTR
print str2

line1 = "interface=wlan0"
line2 = "driver=nl80211"
line3 = str2
line4 = "hw_mode=g"
line5 = "channel=11"


os.chdir("/etc/hostapd")
f = open('hostapd.conf', 'w')
f.write("%s\n%s\n%s%s\n%s\n" % (line1, line2, line3, line4, line5))
f.close()


subprocess.call('sudo ifdown wlan0',shell=True)
subprocess.call('sudo /etc/init.d/networking stop',shell=True)



f=open('/etc/network/interfaces-static')
c=open('/etc/network/interfaces','w')

for line in f:
	print line
	c.write(line)
c.close()
f.close()


#subprocess.call('sudo /etc/init.d/networking start',shell=True)
#subprocess.call('sudo ifup wlan0', shell=True)
#subprocess.call('sudo service isc-dhcp-server start',shell=True)
#subprocess.call('sudo /etc/init.d/apache2 restart',shell=True)

subprocess.call('sudo service hostapd start', shell=True)
subprocess.call('sudo /etc/init.d/networking start', shell=True)

#subprocess.call('sudo ifup wlan0', shell=True)

subprocess.call('sudo service isc-dhcp-server start',shell=True)
