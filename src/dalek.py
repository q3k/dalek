#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import serial
import time
import sys
import atexit

import interfaces

BAUDRATE = 50

LETTERS = {
    "q": 0b11101,
    "w": 0b11001,
    "e": 0b10000,
    "r": 0b01010,
    "t": 0b00001,
    "y": 0b10101,
    "u": 0b11100,
    "i": 0b01100,
    "o": 0b00011,
    u"ó": 0b00011,
    "p": 0b01101,
    "a": 0b11000,
    "s": 0b10100,
    u"ś": 0b10100,
    "d": 0b10010,
    "f": 0b10110,
    "g": 0b01011,
    "h": 0b00101,
    "j": 0b11010,
    "k": 0b11110,
    "l": 0b01001,
    "z": 0b10001,
    u"ż": 0b10001,
    u"ź": 0b10001,
    "x": 0b10111,
    "c": 0b01110,
    u"ć": 0b01110,
    "v": 0b01111,
    "b": 0b10011,
    "n": 0b00110,
    u"ń": 0b00110,
    "m": 0b00111
}

SYMBOLS = {
    "1": 0b11101,
    "2": 0b11001,
    "3": 0b10000,
    "4": 0b01010,
    "5": 0b00001,
    "6": 0b10101,
    "7": 0b11100,
    "8": 0b01100,
    "9": 0b00011,
    "0": 0b01101,
    "-": 0b11000,
    "\b": 0b10100,
#    "$": 0b10010, who are you
    u"ą": 0b10110,
    u"ę": 0b01011,
    u"ł": 0b00101,
    "\b": 0b11010,
    "(": 0b11110,
    ")": 0b01001,
    "+": 0b10001,
    "/": 0b10111,
    ":": 0b01110,
    "=": 0b01111,
    "?": 0b10011,
    ",": 0b00110,
    ".": 0b00111
}

BAUDOT_FIGURES = 0b11011
BAUDOT_LETTERS = 0b11111

BAUDOT_CR = 0b00010
BAUDOT_LF = 0b01000
BAUDOT_SPACE = 0b00100

class Teletype(object):
    def __init__(self, interface):
        self.interface = interface
        self.interface.on()
        self.interface.high()
        time.sleep(1.0)

        self.switch_letters()
        self.column = 0
        self.switch_letters()

    def switch_letters(self):
        self.letters = 1
        self.send_byte(BAUDOT_LETTERS)

    def switch_figures(self):
        self.letters = 0
        self.send_byte(BAUDOT_FIGURES)

    def send_string(self, s):
        for c in s:
            self.send_character(c)

    def send_character(self, character):
        character = character.lower()
        if character == " ":
            self.send_byte(BAUDOT_SPACE)
            self.column += 1
        elif character == "\n":
            self.switch_figures()
            self.send_byte(BAUDOT_CR)
            self.send_byte(BAUDOT_LF)
            self.column = 0
        else:
            if character in LETTERS:
                # letters
                if not self.letters:
                    self.switch_letters()
                self.send_byte(LETTERS[character])
                self.column += 1
            elif character in SYMBOLS:
                if self.letters:
                    self.switch_figures()
                self.send_byte(SYMBOLS[character])
                self.column += 1

        if self.column > 60:
            self.column = 0
            for _ in range(7):
                self.send_byte(BAUDOT_CR)
            self.send_byte(BAUDOT_LF)

    def send_byte(self, byte):
        ta = time.time()
        # start bit (low)
        self.interface.low()
        time.sleep(1.0/BAUDRATE)

        # data bits
        for i in range(5):
            bit = (byte >> (4 - i)) & 1
            if bit > 0:
                self.interface.high()
            else:
                self.interface.low()
            time.sleep(1.0/BAUDRATE)

        # stop bits (high)
        self.interface.high()
        time.sleep(2.0/BAUDRATE)
        #time.sleep(0.5)
        tb = time.time()

        #print "send %f" % (tb - ta)


