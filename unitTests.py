# Imports {{{
from filamentClass import Filament
from printerClass import Printer
from cameraClass import Camera
import progFuncs
import logging as log
# }}}

# LoggingConfig {{{
#log.basicConfig(filename='Automata3D.log', level=log.INFO)
log.basicConfig(level=log.INFO)

# }}}

# User Variables {{{
databaseFile = "Database.pkl"
# }}}

progFuncs.mainMenu(databaseFile)

# progFuncs.changeToRoot()
# printer = Printer("Main", "CR10", [300, 300, 400], 0.4, True)
# filament = Filament("Black ABS", "Hatchbox", "ABS", 1.75, 1.25, 1000, "black")
# camera = Camera("Camera", "Webcam", [1920, 1080])
# progFuncs.linkPrinterAndFilament(printer, filament)
# progFuncs.linkPrinterAndCamera(printer, camera)
# dill.dump_session("Database.pkl")
# # printer.readQRCode()
# filament.createQRCode()
# camera.scanForQRCode()
