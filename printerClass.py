# Imports {{{
import logging as log
import os
import re
import time
from functools import partial
from tkinter.filedialog import askopenfilename
import PIL
import serial
import pyudev
from pyzbar import pyzbar
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
        self.newPrinterUdev()

        self.filament = None
        self.camera = None
        self.jobStart = False
        self.jobStartTime = None
        self.gcode = None
        self.bedClear = True
        # }}}

    # Port {{{
    @property
    def port(self):
        return "/dev/Printers/{}".format(self.name)
    # }}}

    # Serial Port {{{
    @property
    def serial(self):
        try:
            return serial.Serial(self.port, Printer.baudRate)
        except serial.serialutil.SerialException:
            self.newPrinterUdev()
            return serial.Serial(self.port, Printer.baudRate)

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
            grbl_out = self.serial.readline()
            print(' : ' + str(grbl_out.strip()))

        # }}}

    # }}}

    # printSTL {{{
    def printSTL(self):

        # Select file and connect to printer {{{
        input("Press enter to select your file to print.")
        self.gcode = askopenfilename()
        log.info(self.gcode + " has been selected to print")
        self.serial.open()
        # }}}

        with open(self.gcode, "r") as gcode:

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

                # Print the file {{{
                for line in gcode:
                    # Run the remove comment function
                    command = self.removeComment(line)
                    command = command.strip()  # Strip all EOL characters for streaming
                    if (command.isspace() is False and len(command) > 0):
                        log.info("Sending: " + command)
                        self.serial.write((command + '\n').encode())
                        # Wait for response with carriage return
                        grbl_out = self.serial.readline()
                        print(' : ' + str(grbl_out.strip()))
                # }}}

                # Canceled print job {{{
                else:
                    log.warning("Print was canceled")
                    self.serial.close()
                    gcode.close()
                    return False
                # }}}

            # Finished Printing {{{
            input("  Press <Enter> to exit.")
            self.serial.close()  # Close serial port
            self.jobStart = False  # There is no running job
            self.jobStartTime = None  # There is no job time
            log.info(self.gcode + " has completed printing.")  # log it
            self.gcode = None  # Remove gcode file
            # }}}

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
        udevRule = 'SUBSYSTEM == "' + newDevice.subsystem + '", ' \
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

# }}}
