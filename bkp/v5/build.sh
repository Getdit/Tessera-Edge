mkdir -p ~/component_based_v2/build ~/component_based_v2/build/files
cp -r ~/component_based_v2/{boot.py,main.py,component_based,modules} ~/component_based_v2/build/files/.
find ~/component_based_v2/build/files/. -type d -name "__pycache__" -exec rm -rf {} +
mklittlefs -c ~/component_based_v2/build/files/ -b 4096 -p 256 -s 2097152 ~/component_based_v2/build/vfs_novo.bin
cp ~/cb_project/ports/esp32/build-ESP32_GENERIC/firmware.bin ~/component_based_v2/build/.
esptool.py --chip esp32 merge_bin --output ~/component_based_v2/build/firmware_comb.bin 0x1000 ~/component_based_v2/build/firmware.bin 0x200000 ~/component_based_v2/build/vfs_novo.bin