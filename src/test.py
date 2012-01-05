import sys

import interfaces, dalek

usb = interfaces.FuckingUSB()
tty = dalek.Teletype(usb)
tty.send_string(sys.argv[1])
usb.off()
usb.low()
