# Imports {{{
import logging as log
import os
import re
import time
from functools import partial

import PIL
import pyudev
import serial
from pyzbar import pyzbar

import numberToString as NTS

# }}}


# Printer Class {{{
class Printer:

    udevRulesFile = "/etc/udev/rules.d/95-3dprinter.rules"
    addTimeout = 10  # Variable for timeout
    baudRate = 115200

    # Constructor {{{

    def __init__(self, name, model, bldVolume, nozDiam, heatBldPlt):
        # User vars
        self.name = name
        self.model = model
        self.bldVolume = bldVolume  # x y z in mm
        self.nozDiam = nozDiam
        self.heatBldPlt = heatBldPlt
        self.filament = None
        self.camera = None
        self.jobStart = False
        self.jobStartTime = None
        self.bedClear = True
        self.pQueue = []
        self.port = "/dev/Printers/{}".format(self.name)
        try:
            self.serial = serial.Serial(self.port, Printer.baudRate)
        except serial.serialutil.SerialException:
            self.newPrinterUdev()
            self.serial = serial.Serial(self.port, Printer.baudRate)
        self.serial.close()
        # }}}

    # readQRCode {{{

    def readQRCode(self):
        QRimg = PIL.Image.open("cameraScanStub.jpg")
        codes = pyzbar.decode(QRimg)
        # codes = pyzbar.decode(self.camera.scanForQRCode())
        for filamentID in codes:
            return filamentID.data.decode('utf-8')
    # }}}

    # sendCommands {{{
    def sendCommands(self):

        # Command setup {{{
        self.serial.open()
        log.info(self.name + " has been selected")
        self.serial.write("\r\n\r\n".encode())
        time.sleep(2)   # Wait for printer to wake
        self.serial.flushInput()  # Flush startup text in serial input
        log.info(self.name + " is ready to print")
        # }}}

        # Command loop {{{
        while True:
            commandResponse = None
            print("Please input the command you would like to send. To quit send Q")
            command = input("Command: ")

            # Test for quit {{{
            if command == "Q":
                log.info("Quitting out")
                self.serial.close()
                return True
            # }}}

            log.info(self.name + " Sending: " + command)
            self.serial.write((command + '\n').encode())  # Send g-code block
            # Wait for response with carriage return
            self.waitResponse()
        # }}}

    # }}}

    # recordToSD {{{
    def recordToSD(self, filename, gcodeFile):
        commandResponse = None

        self.serial.open()

        with open(gcodeFile, "r") as gcode:

            # Get ready to print {{{
            self.serial.write("\r\n\r\n".encode())
            time.sleep(2)   # Wait for printer to wake
            self.serial.flushInput()  # Flush startup text in serial input
            log.info("Ready to print")
            # }}}

            # Filament used {{{
            for line in gcode:
                if "Filament used:" in line:
                    filUsed = float(re.findall("\d+\.\d+", line)[0])
                    self.jobStart = self.filament.calcRemFil(filUsed)
                    gcode.seek(0)
                    break
                    # Calculate how much filament remains and throw a warning if need be
            # }}}

            if self.jobStart:  # If the job is approved
                self.bedClear = False  # The bed is no longer clear
                self.jobStartTime = time.time()  # The job start time
                self.serial.write(('M21 \n').encode())
                print("M28 {}.gco".format(filename))
                self.serial.write('M21\n'.encode())
                self.waitResponse()
                self.serial.write(('M928 {}.gco\n'.format(filename)).encode())
                self.serial.flush()
                log.info("Started writing {}.gco".format(filename))
                self.waitResponse()

                # Print the file {{{
                counter = 0
                for line in gcode:
                    # Run the remove comment function
                    commandComplete = False
                    command = self.removeComment(line)
                    command = command.strip()  # Strip all EOL characters for streaming
                    if (command.isspace() is False and len(command) > 0):
                        self.serial.write((command + '\n').encode())
                        self.waitResponse()
                        break
                self.serial.write('M29 {}.gco\n'.format(filename).encode())
                log.info("Finished writing {}.gco".format(filename))
                self.serial.flush()
                self.waitResponse()
                # }}}

            # Canceled print job {{{
            else:
                log.warning("Print was canceled")
                self.serial.close()
                gcode.close()
                return False
            # }}}

            # Finished Printing {{{
            self.serial.close()  # Close serial port
            self.jobStart = False  # There is no running job
            self.jobStartTime = None  # There is no job time
            # }}}

    # }}}

    # addToQueue {{{
    def addToQueue(self, filename, gcode):
        filename = NTS.numberToString(filename)
        print(filename)
        self.pQueue.append(filename)
        log.info("{0} has been added to queue for {1}".format(
            filename, self.name))
        self.recordToSD(filename, gcode)

    # }}}

    # Remove comment {{{
    @staticmethod
    def removeComment(string):
        if (string.find(';') == -1):  # If there is no comments
            return string
        else:
            # Otherwise return the stripped string
            return string[:string.index(';')]
    # }}}

    # addPrinterPort {{{
    @staticmethod
    def addPrinterPort():

        # Prompt for new printer {{{
        print("\nYou may only had one printer at a time.")
        input("Please unplug the printer you wish to add. Press enter once complete.\n")
        oldDevices = pyudev.Context()
        log.debug("Old devices found")
        monitor = pyudev.Monitor.from_netlink(oldDevices)
        monitor.filter_by(subsystem='usb')
        log.debug("Monitor started")
        print("Please plugin the printer you wish to add.\n")
        # }}}

        # Poll for new device and return it {{{
        for device in iter(partial(monitor.poll, Printer.addTimeout), None):
            if device.action == 'add':
                print("Printer found")
                log.info("New printer found")
                return device
        # }}}

        log.error("No printer found")
        return None
    # }}}

    # newPrinterUdev {{{
    def newPrinterUdev(self):
        newDevice = Printer.addPrinterPort()
        ruleAlreadyExists = False
        # Udev rule to write {{{
        udevRule = 'SUBSYSTEM == "tty",' \
            'ATTRS{idVendor} == "' + str(newDevice.get('ID_VENDOR_ID')) + '", ' \
            'ATTRS{idProduct} == "' + newDevice.get('ID_MODEL_ID') + '", ' \
            'SYMLINK += "Printers/' + str(self.name) + '"\n'

        # }}} This may not work with multiple printer copies

        try:
            with open(self.udevRulesFile, "r+") as f:
                for line in f:
                    if udevRule == line:
                        log.warning("Udev rule already exists")
                        return None
        except FileNotFoundError:
            log.info("Creating new rule file")

        with open(self.udevRulesFile, "a+") as f:
            f.write(udevRule)
        os.system('sudo su -c "udevadm control --reload-rules && udevadm trigger"')
        time.sleep(2)

    # }}}

    # printInfo {{{
    def printInfo(self):

        bldVStr = 'x'.join(str(e) for e in self.bldVolume)
        print("\nName : {}".format(self.name))
        print("Model : {}".format(self.model))
        print("Build Volume : {}mm".format(bldVStr))
        print("Nozzle diameter : {}mm".format(self.nozDiam))
        print("Heated Build Plate : {}".format(self.heatBldPlt))
        print("Filament Name : {}".format(self.filament))
        print("Camera Name : {}".format(self.camera))
        print("Job Running : {}".format(self.jobStart))
        print("Job Start Time : {}".format(self.jobStartTime))
        print("Bed Clear : {}".format(self.bedClear))
        for i in range(len(self.pQueue)):
            print("Job {0} : {1}".format(i, self.pQueue[i]))

    # }}}

    # monitorPrinter {{{
    def monitorPrinter(self):
        while True:
            grbl_out = self.serial.readline()
            commandResponse = grbl_out.strip().decode("utf-8")
            print(commandResponse)
    # }}}

    # printFromSD {{{
    def printFromSD(self):
        self.serial.open()
        self.serial.write('M32 {}.gco\n'.format(self.pQueue[0]).encode())
        log.info("Started printing {}.gco".format(self.pQueue[0]))
        self.waitResponse()
        log.info("Done printing {}.gco".format(self.pQueue[0]))
        self.serial.close()
        # }}}

    # waitResponse{{{
    def waitResponse(self):
        commandResponse = None
        while commandResponse != "ok":
            grbl_out = self.serial.readline()
            commandResponse = grbl_out.strip().decode("utf-8")
            print(commandResponse)
    # }}}


# }}}
