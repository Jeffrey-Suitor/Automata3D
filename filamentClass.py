# Imports {{{
from datetime import datetime
import math
import logging as log
import uuid
import pyqrcode
from PIL import Image, ImageDraw, ImageFont
import os
# }}}


# Filament Class {{{
class Filament:

    fontPath = "/usr/share/fonts/nerd-fonts-complete/ttf/mononoki-Regular Nerd Font Complete Mono.ttf"
    qrDir = "qrCodes"
    filamentTypeFile = "filamentTypes.txt"
    filamentColourFile = "filamentColour.txt"

    if not os.path.exists(qrDir):
        os.mkdir(qrDir)

    if not os.path.exists(filamentTypeFile):
        open(filamentTypeFile, 'w+').close()

    if not os.path.exists(filamentColourFile):
        open(filamentColourFile, 'w+').close()

    # Constructor {{{

    def __init__(self, name, company, mat, matDia, density, remFil, colour,):
        # User vars
        self.name = name
        self.company = company
        self.mat = mat
        self.matDia = matDia  # In mm
        self.density = density  # In g/cm^3
        self.remFil = remFil  # In grams
        self.colour = colour

        self.printer = None
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.id = str(uuid.uuid4())
        # }}}

    # calcRemFil {{{
    def calcRemFil(self, usedFil):

        choice = None
        usedFil = usedFil*100  # convert to cm from m
        crossSecArea = (self.matDia/10/2)**2 * math.pi()  # /10 for mm to cm
        volUsed = crossSecArea * usedFil  # volUsed in cm
        gramsUsed = volUsed * self.density  # grams used

        # Filament runout warning {{{
        if self.remFil - gramsUsed < 0:

            log.warning('This print will run out of filament.')
            while choice not in ('y', 'Y', 'n', 'N'):
                choice = input('Do you wish to proceed with the print? y/n : ')

                if choice == 'y' or choice == 'Y':  # Use currently generated reports
                    self.remFil -= gramsUsed  # Record the change
                    log.info("YES, continue print job")
                    return True

                elif choice == 'n' or choice == 'N':  # Generate new reports
                    log.info("NO, cancel print")
                    return False

                else:
                    print('This is not a valid selection')

                    # }}}

        # Filament almost out warning {{{
        elif self.remFil - gramsUsed < 3:

            log.warning("This print nearly run out of filament."
                        "There will be {0} left over"
                        .format(self.remFil - gramsUsed))
            while choice not in ('y', 'Y', 'n', 'N'):
                choice = input('Do you wish to proceed with the print? y/n : ')

                if choice == 'y' or choice == 'Y':  # Use currently generated reports
                    self.remFil -= gramsUsed  # Record the change
                    log.info("YES, continue print job")
                    return True

                elif choice == 'n' or choice == 'N':  # Generate new reports
                    log.info("NO, cancel print")
                    return False

                else:
                    print('This is not a valid selection')

        # }}}

        # Proceed with print {{{
        else:
            self.remFil -= gramsUsed  # Record the change
            log.info("{0}g of filament remaining.".format(self.remFil))
            return True
        # }}}

    # }}}

    # createQRCode {{{
    def createQRCode(self):

        tempFile = 'temp.png'

        code = pyqrcode.create(self.id)
        code.png(tempFile, scale=5)

        # Adds caption
        qrCode = Image.open(tempFile)
        img = Image.new('RGB', (800, 250), color=(255, 255, 255))
        img.paste(qrCode, (10, 10))
        draw = ImageDraw.Draw(img)
        fnt = ImageFont.truetype(Filament.fontPath, 19)

        msg = "Name         : " + self.name + "\n" \
              "Maker        : " + self.company + "\n" \
              "Material     : " + self.mat + "\n" \
              "Diameter     : " + str(self.matDia) + "mm\n" \
              "Density      : " + str(self.density) + "g/cm^3\n" \
              "Weight       : " + str(self.remFil) + "kg\n" \
              "Colour       : " + self.colour + "\n" \
              "Date Added   : " + self.date + "\n" \
              "ID           : " + self.id + "\n"

        draw.text((250, 28), msg, font=fnt, fill=(0, 0, 0))
        img.save(Filament.qrDir + "/" + self.name + "_" + self.id + "_QR.png")
        os.remove(tempFile)
    # }}}

# }}}
