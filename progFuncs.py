import logging as log
import os
import sys


# linkPrinterandCamera {{{
def linkPrinterAndCamera(printer, camera):
    log.info("Linking PRINTER : {0} CAMERA : {1}"
             .format(printer.name, camera.name))
    printer.camera = camera
    camera.printer = printer
    return True

# }}}

# linkPrinterAndFilament {{{


def linkPrinterAndFilament(printer, filament):
    log.info("Linking PRINTER : {0} FILAMENT : {1}"
             .format(printer.name, filament.name))
    printer.filament = filament
    filament.printer = printer
    return True

# }}}

# changeToRoot {{{


def changeToRoot():
    if os.geteuid() != 0:
        os.execvp("sudo", ["sudo", "python3"] + sys.argv)

# }}}
