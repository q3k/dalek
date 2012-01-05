import socket
import os
import struct
import time

import dalek
import interfaces
import config

class DalekDaemon(object):
    def __init__(self):
        self.interface = None
        self.teletype = None

    def start(self, configpath="/etc/dalek.conf"):
        self.config = config.Configuration(configpath)
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        interface_name = self.config.interface

        if interface_name == "usb":
            self.interface = interfaces.FuckingUSB()
        # TODO: implement more interfaces

        if not self.interface:
            raise Exception("No interface created! Are you sure you used a correct one?")

        self.teletype = dalek.Teletype(self.interface)

        if os.path.exists(self.config.daemon_socket):
            os.remove(self.config.daemon_socket)

        print "Binding to %s..." % self.config.daemon_socket
        self.socket.bind(self.config.daemon_socket)
        self.socket.listen(1)
        self.socket.settimeout(1.0)

        last_time_on = time.time()
        teletype_on = True
        while True:
            try:
                s, a = self.socket.accept()
            except socket.timeout:
                if time.time() - last_time_on > int(self.config.motor_timeout):
                    self.interface.off()
                    self.interface.low()
                    teletype_on = False
                    time.sleep(int(self.config.motor_spindown))
                continue

            s.settimeout(2.0)
            message_type = ""
            try:
                message_type = s.recv(1)
            except socket.timeout:
                print "Timeout when receiving message type... continuing."
                try:
                    s.send(chr(2))
                    s.close()
                except:
                    pass
            except:
                print "Error when receiving message type... continuing."
                continue

            if message_type == "m":
                if not teletype_on:
                    self.interface.on()
                    self.interface.high()
                    teletype_on = True
                    last_time_on = time.time()
                    time.sleep(int(self.config.motor_spinup))
                # send message to teletype
                try:
                    length_bin = s.recv(4)
                except socket.timeout:
                    print "Timeout when receiving text length..."
                    try:
                        s.send(chr(2))
                        s.close()
                    except:
                        pass
                except:
                    print "Error when receiving text length..."
                    continue

                length = struct.unpack("!I", length_bin)[0]
                if length > 4096:
                    print "message over 4096 characters... ignoring."
                    s.send(chr(1))
                    s.close()
                    continue

                data = ""
                left_to_receive = length
                while left_to_receive > 0:
                    try:
                        new_data = s.recv(left_to_receive)
                    except socket.timeout:
                        print "Timeout when receiving text block..."
                        try:
                            s.send(chr(2))
                            s.close()
                        except:
                            pass

                    left_to_receive -= len(new_data)
                    data += new_data

                try:
                    self.teletype.send_string(data)
                except:
                    print "Error when talking to teletype... Recreating interface."
                    raise Exception("The interface just crashed.")
                    #TODO: Recreate interface and recover it

                try:
                    s.send(chr(0))
                    s.close()
                except:
                    pass
                last_time_on = time.time()
                continue

            try:
                s.send(chr(1))
                s.close()
            except:
                pass

if __name__ == "__main__":
    d = DalekDaemon()
    d.start()
