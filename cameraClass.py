# Imports {{{
import logging as log
import pyudev
import os
from functools import partial
import time
import cv2
# }}}


# Camera Class {{{
class Camera:

    udevRulesFile = "/etc/udev/rules.d/90-3dprintercamera.rules"
    addTimeout = 10  # Variable for timeout

    # Constructor {{{

    def __init__(self, name, model, resolution):
        # User vars
        self.name = name
        self.model = model
        self.resolution = resolution
        self.printer = None
        self.port = "/dev/Cameras/" + self.name
        # self.newCameraUdev()
        # }}}

    # addCameraPort {{{
    @staticmethod
    def addCameraPort():

        # Prompt for new camera {{{
        print("\nYou may only had one camera at a time.")
        input("Please unplug the camera you wish to add. Press enter once complete.\n")
        oldDevices = pyudev.Context()
        log.debug("Old devices found")
        monitor = pyudev.Monitor.from_netlink(oldDevices)
        monitor.filter_by(subsystem='usb')
        log.debug("Monitor started")
        print("Please plugin the camera you wish to add.\n")
        # }}}

        # Poll for new device and return it {{{
        for device in iter(partial(monitor.poll, Camera.addTimeout), None):
            if device.action == 'add':
                print("Camera found")
                log.info("New camera found")
                return device
        # }}}

        log.error("No camera found")
        return None
    # }}}

    # newCameraUdev {{{
    def newCameraUdev(self):
        newDevice = Camera.addCameraPort()
        ruleAlreadyExists = False
        # Udev rule to write {{{
        udevRule = 'SUBSYSTEM == "video4linux", ' \
            'ATTRS{idVendor} == "' + str(newDevice.get('ID_VENDOR_ID')) + '", ' \
            'ATTR{index} == "0", ' \
            'ATTRS{idProduct} == "' + newDevice.get('ID_MODEL_ID') + '", ' \
            'SYMLINK += "Cameras/' + str(self.name) + '"\n'

        # }}} This may not work with multiple camera copies

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

    # scanForQRCode{{{
    def scanForQRCode(self):
        cap = cv2.VideoCapture(self.port)
        if cap.isOpened():
            log.info("Connected to camera")
            ret, frame = cap.read()
            rgbImage = frame
            return rgbImage
        else:
            print("not valid")
        # }}}

    # showVideoStream {{{
    def showVideoStream(self):
        print("Welcome to the video preview.\n"
              "Press r to rotate the video 90.\n"
              "Press v to flip the video vertically.\n"
              "Press h to flip the video horizontally.\n"
              "Press q to quit.\n")
        cam = cv2.VideoCapture(self.port)
        while True:
            rotate, horflip, verflip = False
            ret_val, img = cam.read()
            if rotate:
                img = cv2.rotate(img, 90)
            if horflip:
                img = cv2.flip(img, 1)
            if verflip:
                img = cv2.flip(img, 0)
            cv2.imshow(self.printer.name, img)
            key = cv2.waitKey(1)
            if key == ord('r'):  # check for rotate
                rotate = not rotate
            elif key == ord('h'):  # check for horizontal flip
                horflip = not horflip
            elif key == ord('v'):  # check for vertical flip
                verflip = not verflip
            elif key == ord('q'):
                log.info("Leaving camera menu")
                break
            else:
                print("Not a valid key")

        cv2.destroyAllWindows()
# }}}

        # }}}
