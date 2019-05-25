from filamentClass import Filament
from printerClass import Printer
import progFuncs

progFuncs.changeToRoot()
printer = Printer("Main", "CR10", [300, 300, 400], 0.4, True)
filament = Filament("Black ABS", "Hatchbox", "ABS", 1.75, 1.25, 1000, "black")
progFuncs.linkPrinterAndFilament(printer, filament)
filament.createQRCode()
