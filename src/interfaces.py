import sys
import time

try:
    import portio
except:
    # gotta catch em all
    pass

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


class VIAGPIO(DummyInterface):
    def __init__(self):
        if portio.ioperm(0x123, 1, 1):
	    raise Exception("Could not gain IO permissions!")
        self.value = 0
	portio.outb(self.value, 0x123)
    
    def high(self):
        self.value |= 0b01000000
        portio.outb(self.value, 0x123)

    def low(self):
        self.value &= 0b10111111
        portio.outb(self.value, 0x123)

    def on(self):
        self.value |= 0b00100000
        portio.outb(self.value, 0x123)

    def off(self):
        self.value &= 0b11011111
        portio.outb(self.value, 0x123)


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
        import usb.core
        try:
            self.dev.ctrl_transfer(0x20, 0x09, 0x0300 | byte, 0, chr(byte), 5000);
        except usb.core.USBError:
            dev = usb.core.find(idVendor=self.VID, idProduct=self.PID)
            if not dev:
                print "Interface seems to be down... Waiting 10 seoncds then trying again."
                time.sleep(10)
                dev = usb.core.find(idVendor=self.VID, idProduct=self.PID)
                if not dev:
                    print "Teletype still nor present! Failing."
                    raise Exception("Teletype not present.")
            self.dev = dev
            self.set_device_byte(byte)


    def high(self):
        self.set_device_byte(2)

    def low(self):
        self.set_device_byte(1)

    def on(self):
        self.set_device_byte(4)

    def off(self):
        self.set_device_byte(3)
