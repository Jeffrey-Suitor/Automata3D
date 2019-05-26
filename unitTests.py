from filamentClass import Filament
from printerClass import Printer
from cameraClass import Camera
import progFuncs

progFuncs.changeToRoot()
printer = Printer("Main", "CR10", [300, 300, 400], 0.4, True)
filament = Filament("Black ABS", "Hatchbox", "ABS", 1.75, 1.25, 1000, "black")
camera = Camera("Camera", "Webcam", [1920, 1080])
progFuncs.linkPrinterAndFilament(printer, filament)
progFuncs.linkPrinterAndCamera(printer, camera)
printer.readQRCode()
# filament.createQRCode()
# camera.scanForQRCode()
