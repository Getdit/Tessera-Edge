import network, mip

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Galaxy_Eduardo', '123quatro')

mip.install("urequests")