#!/bin/python

# Script upload and runs "echo" program to the STM32 with WiFi expnasion board.
# The connection is following: Wi-Fi board <--> STM32 <--> PC. STM32 is used
# only as middleman and do nothing.
# Then, scripts list HTML/CSS files in the "dir" and upload them to the
# Wi-Fi expansion board. Further those files are used for web-server.

import os
import sys
import time
import serial
import subprocess
from time import sleep
from pprint import pprint

from AT import IDW01M1, ATException

#===============================================================================
# Configuration
#===============================================================================
# Serial port
port = "/dev/ttyACM0"
# Server folder
srv_dir = '/srv/http'

host = '192.168.12.1'
#===============================================================================
# Directory with web content
web_dir = "./web"
# Serial port baudrate
baud = 115200
# SSID
ssid = "*********"
# Password
password = "********"
# Network privacy mode
# 0 - none, 1 - WEP, 2 - WPA-Personal (TKIP/AES) or WPA2-Personal(TKIP/AES)
priv_mode=2
# Network mode
# 1 - STA, 2 - IBSS, 3 - MiniAP
wifi_mode=1
# Name of the image file
img_name = 'outfile.img'
# Name of the image generator
img_gen = 'httpd_gen.o'

cur_dir = os.path.dirname(os.path.abspath(__file__))

#===============================================================================
# Convert path
#===============================================================================
srv_dir = os.path.abspath(srv_dir)
web_dir = os.path.abspath(web_dir)
img_gen = '{}/{}'.format(cur_dir, img_gen)

def file_list(path):
    """List files and their sizes in `path`.

    Args:
        path: path to directory with files

    Returns:
        List of lists [['filename', filesize], ['filename', filesize]]
    """
    files = [[f, os.path.getsize(os.path.join(path, f))] for f in os.listdir(
        path) if os.path.isfile(os.path.join(path, f))]

    return files

if __name__ == '__main__':
    print("X-NUCLEO-IDW01M1 web-server updater\n")

    print('Files to pack into image [\'filename\', filesize]:')
    pprint(file_list(web_dir))

    # NOTE: For subfolders add */*
    cmd = 'cd {}; rm -f {}; {} {} *.*'.format(web_dir, img_name, img_gen, 
            img_name)
    print('Generating image by "{}".'.format(cmd))
    rc = subprocess.call(cmd, shell=True)
    if rc != 0:
        print('Can\'t generate image. Using: {}'.format(cmd))

    cmd = "cp {}/{} {}/{}".format(web_dir, img_name, srv_dir, img_name)
    print('Copy image file to server directory.')
    subprocess.call(cmd, shell=True)
    if rc != 0:
        print('Can\'t copy image file {}/{} to the {}. Using: {}'.format(
              web_dir, img_name, srv_dir, cmd))

    print('Connect to the serial port "{}"'.format(port))
    with serial.Serial(port, baud, timeout=None) as ser:
        
        ser = serial.serial_for_url(port, baudrate=baud, timeout=1)
        ser.flush()
    
        with serial.threaded.ReaderThread(ser, IDW01M1) as module:
            try:
                module.send_at()
    
                print(('Configuring Wi-Fi credentials. SSID: {} PASSWORD: '
                       '{}').format(ssid, password))
                module.configure_wifi(ssid, password)
                module.save_configuration()
                module.reset()

                module.read_until(
                        'WiFi Association with \'{}\' successful'.format(ssid))
                module.read_until('+WIND:24:WiFi', timeout=10)

                print('Erase eternal Flash memory of the module')
                module.erase_extmem()

                print('Upload filesystem Image "{}/{}"'.format(srv_dir, 
                    img_name))
                module.update_fs(host, "/{}".format(img_name))
    
                sleep(2)

                print('Current list of files on the board:')
                pprint(module.get_file_list())

                module.reset()

            except ATException as e:
                print(e)
