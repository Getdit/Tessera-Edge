import network, mip

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Eduardo', 'sao5Reais')

mip.install("urequests")