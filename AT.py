#! /usr/bin/env python
# encoding: utf-8
"""
Example of a AT command protocol.

https://en.wikipedia.org/wiki/Hayes_command_set
http://www.itu.int/rec/T-REC-V.250-200307-I/en

Code is taken from: 
    https://github.com/pyserial/pyserial/blob/master/examples/at_protocol.py
"""
import sys
sys.path.insert(0, '..')

import time
import logging
import binascii
import serial
import serial.threaded
import threading

try:
    import queue
except ImportError:
    import Queue as queue


class ATException(Exception):
    pass


class ATProtocol(serial.threaded.LineReader):

    TERMINATOR = b'\r\n'

    def __init__(self):
        super(ATProtocol, self).__init__()
        self.alive = True
        self.responses = queue.Queue()
        self.events = queue.Queue()
        self._event_thread = threading.Thread(target=self._run_event)
        self._event_thread.daemon = True
        self._event_thread.name = 'at-event'
        self._event_thread.start()
        self.lock = threading.Lock()
        self.unhandled_events = queue.Queue()

    def stop(self):
        """
        Stop the event processing thread, abort pending commands, if any.
        """
        self.alive = False
        self.events.put(None)
        self.responses.put('<exit>')

    def _run_event(self):
        """
        Process events in a separate thread so that input thread is not
        blocked.
        """
        while self.alive:
            try:
                self.handle_event(self.events.get())
            except:
                logging.exception('_run_event')

    def handle_line(self, line):
        """
        Handle input from serial port, check for events.
        """
        if line.startswith('+'):
            self.events.put(line)
        else:
            self.responses.put(line)

    def handle_event(self, event):
        """
        Spontaneous message received.
        """
        print('event received:', event)

    def command(self, command, response='OK', timeout=5):
        """
        Set an AT command and wait for the response.

        Args:
            command: AT command
            response: expected response
            timeout: timeout

        Returns:
            List of read preceding lines before response

        Raises:
            ATException: In case of timeout
        """
        # ensure that just one thread is sending commands at once
        with self.lock:  
            # print("CMD: {}".format(command))
            self.write_line(command)
            lines = []
            while True:
                try:
                    line = self.responses.get(timeout=timeout)
                    # print("{}".format(line))
                    if line == response:
                        return lines
                    else:
                        lines.append(line)
                except queue.Empty:
                    raise ATException('AT command timeout ({!r})'.format(
                            command))

    def read_until(self, pattern='OK', timeout=5):
        lines = []
        while True:
            try:
                line = self.unhandled_events.get(timeout=timeout)
                # print("{}".format(line))
                if pattern in line:
                    return lines
                else:
                    lines.append(line)
            except queue.Empty:
                raise ATException(
                        'Pattern not found. Timeout ({!r}).\n{}'.format(
                        pattern, lines))


class IDW01M1(ATProtocol):
    """
    AT interface for ST Wi-Fi expansion board X-NUCLEO-IDW01M1

    https://os.mbed.com/components/X-NUCLEO-IDW01M1/
    """

    def __init__(self):
        super(IDW01M1, self).__init__()
        self.event_responses = queue.Queue()
        self._awaiting_response_for = None

    def connection_made(self, transport):
        super(IDW01M1, self).connection_made(transport)
        # our adapter enables the module with RTS=low
        self.transport.serial.rts = False
        time.sleep(0.3)
        self.transport.serial.reset_input_buffer()

    def handle_event(self, event):
        """Handle events and command responses starting with '+...'"""
        if event.startswith('+RRBDRES') and self._awaiting_response_for.startswith('AT+JRBD'):
            rev = event[9:9 + 12]
            mac = ':'.join('{:02X}'.format(ord(x)) for x in rev.decode('hex')[::-1])
            self.event_responses.put(mac)
        else:
            self.unhandled_events.put(event)
            logging.warning('unhandled event: {!r}'.format(event))

    def command_with_event_response(self, command):
        """Send a command that responds with '+...' line"""
        # ensure that just one thread is sending commands at once
        with self.lock:  
            self._awaiting_response_for = command
            self.transport.write(b'{}\r\n'.format(
                command.encode(self.ENCODING, self.UNICODE_HANDLING)))
            response = self.event_responses.get()
            self._awaiting_response_for = None
            return response

    def write(self, data):
        with self.lock:
            self.write_line(data)

    def send_at(self):
        """Send `AT` command and do nothing
        """
        self.command("AT")

    def configure_wifi(self, ssid, password, priv_mode=2, wifi_mode=1):
        """Configure module to connect specific Wi-Fi AP
         
        Args:
            ssid: Name of the AP
            password: password for the AP
            priv_mode: Network privacy mode 0 - none, 1 - WEP, 2 -
                WPA-Personal (TKIP/AES) or WPA2-Personal(TKIP/AES)
            wifi_mode: Network mode 1 - STA, 2 - IBSS, 3 - MiniAP
        """
        self.command("AT+S.SSIDTXT={}\r\n".format(ssid))
        self.command("AT+S.SCFG=wifi_wpa_psk_text,{}\r\n".format(password))
        self.command("AT+S.SCFG=wifi_priv_mode,{}\r\n".format(priv_mode))
        self.command("AT+S.SCFG=wifi_mode,{}\r\n".format(wifi_mode))

    def save_configuration(self):
        self.command("AT&W")

    def reset(self):
        self.command("AT+CFUN=1", response='')

    def get_file_list(self):
        return list(filter(None, self.command("AT+S.FSL")))

    def erase_extmem(self):
        self.command('AT+S.HTTPDFSERASE')

    def update_fs(self, host, img_name):
        self.command('AT+S.HTTPDFSUPDATE={},{}'.format(host, img_name), 
                response='')

