esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z --flash_mode dio --flash_freq 40m 0x00 ~/component_based_v2/build/firmware_comb.bin
mpremote repl