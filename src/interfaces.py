import sys

class InterfaceException(Exception):
    pass

class DummyInterface(object):
    def __init__(self):
        pass

    def high(self):
        pass

    def low(self):
        pass

    def on(self):
        pass

    def off(self):
        pass

class BusPirate(DummyInterface):
    def __init__(self, port):
        import serial

        try:
            self.s = serial.Serial(port, 115200)
        except:
            raise InterfaceException("Could not open serial port!")

        self.s.write("m 6 1 2\r\n")

    def high(self):
        self.s.write("-\r\n")

    def low(self):
        self.s.write("_\n")

class FuckingUSB(DummyInterface):
    VID = 0x16c0
    PID = 0x05df

    def __init__(self):
        import usb.core
        import usb.util

        dev = usb.core.find(idVendor=self.VID, idProduct=self.PID)
        if not dev:
            raise InterfaceException("Teletype not found!")

        manufacturer = usb.util.get_string(dev, 256, dev.iManufacturer)
        product = usb.util.get_string(dev, 256, dev.iProduct)

        self.dev = dev

    def set_device_byte(self, byte):
        self.dev.ctrl_transfer(0x20, 0x09, 0x0300 | byte, 0, chr(byte), 5000);

    def high(self):
        self.set_device_byte(2)

    def low(self):
        self.set_device_byte(1)

    def on(self):
        self.set_device_byte(4)

    def off(self):
        self.set_device_byte(3)
