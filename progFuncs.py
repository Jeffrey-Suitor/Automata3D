# Imports {{{
import logging as log
import os
import sys
from filamentClass import Filament
from printerClass import Printer
from cameraClass import Camera
from datetime import datetime
import pickle
# }}}

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


# Create Devices {{{

# createPrinter {{{
def createPrinter(printerList):
    choice = None

    # Prompt {{{
    name = input("What is the name of this printer : ")
    model = input("What model of printer is this : ")
    print("Please enter your build volume in the order of X, Y, Z")
    xVolume = int(input("What is the build volume of your printer (X) : "))
    yVolume = int(input("What is the build volume of your printer (Y) : "))
    zVolume = int(input("What is the build volume of your printer (Z) : "))
    bldVolume = [xVolume, yVolume, zVolume]
    nozDiam = float(input("What is your nozzle diameter in mm : "))
    # }}}

    # heatedBuildPlate {{{
    while choice not in ('y', 'Y', 'n', 'N'):
        choice = input('Is your build plate heated y/n : ')
        if choice == 'y' or choice == 'Y':  # Use currently generated reports
            heatedBuildPlate = True
        elif choice == 'n' or choice == 'N':  # Generate new reports
            heatedBuildPlate = False
        else:
            print('This is not a valid selection')

    # }}}

    # logFile {{{
    log.info("A printer with the following properties has been added:\n"
             "Name -> " + name + "\n"
             "Model -> " + name + "\n"
             "Build volume -> " + str(xVolume) + "x" +
             str(yVolume) + "x" + str(zVolume) + "\n"
             "Nozzle diameter -> " + str(nozDiam) + "\n"
             "Heated build plate -> " + str(heatedBuildPlate) + "\n")

    # }}}

    instance = Printer(name, model, bldVolume, nozDiam, heatedBuildPlate)
    printerList.append(instance)

# }}}


# createFilament {{{
def createFilament(filamentList):
    choice = None

    # Prompt {{{
    name = input("What is the name of this filament : ")
    company = input("Who makes this filament : ")
    mat = input("What type of material is this filament : ")
    matDia = input("What is the diameter of this filament in mm : ")
    density = input("What is the density of this filament in g/cm^3 : ")
    weight = input("What is the weight of this filament in g : ")
    colour = input("What colour is this filament : ")
    # }}}

    # logFile {{{
    log.info("A filament with the following properties has been added:\n"
             "Name -> " + name + "\n"
             "Company -> " + company + "\n"
             "Material -> " + mat + "\n"
             "Material diameter -> " + matDia + "mm\n"
             "Density -> " + density + "g/cm^3\n"
             "Weight -> " + weight + "g\n"
             "Colour -> " + colour + "\n")
    # }}}

    instance = Filament(name, company, mat, matDia, density, weight, colour)
    filamentList.append(instance)

# }}}


# createCamera {{{
def createCamera(cameraList):
    choice = None

    # Prompt {{{
    name = input("What is the name of this printer : ")
    model = input("What model of printer is this : ")
    resolution = input("What is the resolution of this camera : ")
    # }}}

    # logFile {{{
    log.info("A printer with the following properties has been added:\n"
             "Name -> " + name + "\n"
             "Model -> " + model + "\n"
             "Resolution -> " + resolution + "\n")

    # }}}

    instance = Camera(name, model, resolution)
    cameraList.append(instance)

# }}}

# }}}


# changeToRoot {{{


def changeToRoot():
    if os.geteuid() != 0:
        os.execvp("sudo", ["sudo", "python3"] + sys.argv)
# }}}


# checkDatabase {{{
def checkDatabase(databaseFile):
    if not os.path.exists(databaseFile):
        mainList = [[] for i in range(3)]
        log.info("Creating new database")
        with open(databaseFile, "wb") as f:
            pickle.dump(mainList, f)
        return mainList
    else:
        log.info('Opening the "{}" database file.'.format(databaseFile))
        with open(databaseFile, "rb") as f:
            mainList = pickle.load(f)
        return mainList
# }}}


# mainMenu{{{
def mainMenu(databaseFile):

    # Initialization {{{
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M")
    log.info('New session started : {}'.format(currentTime))
    mainList = checkDatabase(databaseFile)
    print(mainList)
    choice = None
    # }}}

    while choice != 6:
        # Prompt {{{
        print("\n\nAutomata3d : Printer Management Software\n\n\n"
              "Please select the number next to the option you would like\n\n"
              "1. Begin print job\n"
              "2. View printer status\n"
              "3. Access filament library\n"
              "4. View cameras\n"
              "5. Add a new printer / filament / camera\n"
              "6. Exit\n")
        # }}}
        try:
            choice = int(input('What would you like to do : '))
            if choice == 1:
                print("Start print")
            if choice == 2:
                print("Select your printer")
            if choice == 3:
                print("Access filament library")
            if choice == 4:
                print("View cameras")
            if choice == 5:
                log.info("Accessing device creation menu")
                addDeviceMenu(databaseFile, mainList)
            if choice == 6:
                # Close program {{{
                print("Have a great day.")
                with open(databaseFile, "wb") as f:
                    pickle.dump(mainList, f)
                    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M")
                    log.info('Session closed at : {}'.format(currentTime))
                    exit()
        except ValueError:
            log.warning("Not a valid selection.")
    # }}}
# }}}


# addDeviceMenu {{{
def addDeviceMenu(databaseFile, mainList):

    choice = None
    while choice != 4:

        # Prompt {{{
        print("\n\nWhat device would you like to add ?\n\n\n"
              "Please select the number next to the option you would like\n\n"
              "1. Printer\n"
              "2. Filament\n"
              "3. Camera\n"
              "4. Return to main menu\n")
        # }}}

        choice = int(input('What would you like to do : '))
        if choice == 1:
            log.info("Adding new printer")
            createPrinter(mainList[0])
        if choice == 2:
            log.info("Adding new filament spool")
            createFilament(mainList[1])
        if choice == 3:
            log.info("Adding new camera")
            createCamera(mainList[2])
        if choice == 4:
            log.info("Returning to main menu")
            return

        with open(databaseFile, "wb") as f:
            pickle.dump(mainList, f)
# }}}
