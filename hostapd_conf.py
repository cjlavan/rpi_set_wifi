import os

f=open('/sys/class/net/wlan0/address')
MACADD = f.readline()
f.close


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
