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
            heatBldPlt = True
        elif choice == 'n' or choice == 'N':  # Generate new reports
            heatBldPlt = False
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

    instance = Printer(name, model, bldVolume, nozDiam, heatBldPlt)
    printerList.append(instance)

# }}}


# createFilament {{{
def createFilament(filamentList):
    choice = None

    # Prompt {{{
    name = input("What is the name of this filament : ")
    company = input("Who makes this filament : ")
    mat = input("What type of material is this filament : ")
    matDia = float(input("What is the diameter of this filament in mm : "))
    density = float(input("What is the density of this filament in g/cm^3 : "))
    weight = int(input("What is the weight of this filament in g : "))
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
    name = input("What is the name of this camera : ")
    model = input("What model of camera is this : ")
    xRes = int(input("X resolution : "))
    yRes = int(input("Y resolution : "))
    resolution = [xRes, YRes]
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

    while choice != 7:
        # Prompt {{{
        print("\n\nAutomata3d : Printer Management Software\n\n\n"
              "Please select the number next to the option you would like\n\n"
              "1. Begin print job\n"
              "2. View printer status\n"
              "3. Edit properties\n"
              "4. View cameras\n"
              "5. Add a new printer / filament / camera\n"
              "6. Remove printer /filament / camera\n"
              "7. Exit\n")
        # }}}
        try:
            choice = int(input('What would you like to do : '))
            if choice == 1:
                print("Start print")
            elif choice == 2:
                print("Select your printer")
            elif choice == 3:
                log.info("Editing properties")
                editPropertiesMenu(mainList)
            elif choice == 4:
                log.info("Viewing cameras")
                checkCamerasMenu(mainList)
            elif choice == 5:
                log.info("Accessing device creation menu")
                addDeviceMenu(databaseFile, mainList)
            elif choice == 6:
                log.info("Device deletion menu")
                deleteMenu(databaseFile, mainList)
            elif choice == 7:
                # Close program {{{
                print("Have a great day.")
                with open(databaseFile, "wb") as f:
                    pickle.dump(mainList, f)
                    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M")
                    log.info('Session closed at : {}'.format(currentTime))
                    exit()
        except ValueError:
            log.warning("Not a valid selection")
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
              "4. Link printer and filament\n"
              "5. Link printer and camera\n"
              "6. Return to main menu\n")
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
            log.info("Linking printer and filament")
            linkMenu(mainList[0], mainList[1], "filament")
        if choice == 5:
            log.info("Linking printer and camera")
            linkMenu(mainList[0], mainList[2], "camera")
        if choice == 6:
            log.info("Returning to main menu")
            return

        with open(databaseFile, "wb") as f:
            pickle.dump(mainList, f)
# }}}


# deleteMenu {{{
def deleteMenu(databaseFile, mainList):

    choice = None
    while choice != 4:

        # Prompt {{{
        print("\n\nWhat device would you like to remove ?\n\n\n"
              "Please select the number next to the option you would like\n\n"
              "1. Printer\n"
              "2. Filament\n"
              "3. Camera\n"
              "4. Return to main menu\n")
        # }}}

        choice = int(input('What would you like to do : '))
        if choice == 1:
            log.info("Deleting printer")
            deleteDevice(mainList[0], "Printer")
        if choice == 2:
            log.info("Deleting filament spool")
            deleteDevice(mainList[1], "Filament")
        if choice == 3:
            log.info("Deleting camera")
            deleteDevice(mainList[2], "Camera")
        if choice == 4:
            log.info("Returning to main menu")
            return

        with open(databaseFile, "wb") as f:
            pickle.dump(mainList, f)
# }}}


# deleteDevice {{{
def deleteDevice(devList, devType):
    choice = None
    if len(devList) == 0:  # Check if no devices
        log.warning("There are no {}s created yet.".format(devType))
        return
    while choice != len(devList)+1:  # as long as user doesnt quit
        print("What {} would you like to remove:".format(devType))
        for i in range(len(devList)):  # print entire dev list
            print("{0}. {1}".format(i+1, devList[i].name))
        print("{}. Quit".format(i+2))  # print quit
        choice = int(input("Select the number of the device  to remove : "))
        if 0 < choice <= len(devList):  # if the user selects a device
            if confirmationPrompt():  # Confirm the user chioce
                log.info("Removing {}".format(devList[choice-1].name))
                del devList[choice-1]  # Delete the device
        elif choice == len(devList)+1:
            log.info("Returning to remove menu")
            return
        else:
            print("This is not a valid selection")
            # }}}


# confirmationPrompt {{{
def confirmationPrompt():
    choice = None
    while choice not in ("y", "Y", "n", "N"):
        choice = input("Please confirm your selection (y/n) : ")
        if choice == "y" or choice == "Y":
            log.info("Choice confirmed")
            return True
        elif choice == "n" or choice == "N":
            log.info("Choice canceled")
            return False
        else:
            print("This is not a valid selection")
# }}}


# checkCamerasMenu{{{
def checkCamerasMenu(mainList):
    choice = None

    if len(mainList[0]) == 0:  # Check if no devices
        log.warning("There are no Printers created yet.")
        return
    elif len(mainList[2]) == 0:  # Check if no devices
        log.warning("There are no Cameras created yet.")
        return
    while True:
        print("What Printer would you like to view.")
        printer = itemSelectionMenu(mainList[0], "Printer")
        if printer is None:
            log.warning("No printer selected returning to main menu.")
            return
        elif printer.camera is None:  # Check if camera conncted
            log.warning("No camera detected for {}.".format(printer.name))
        else:
            printer.camera.showVideoStream()
# }}}


# linkMenu {{{
def linkMenu(printers, devices, devType):

    print("What Printer would you like to link.")
    selectedPrinter = itemSelectionMenu(printers, "Printer")
    print("What {} would you like to link.".format(devType))
    chosenDevice = itemSelectionMenu(printers, devType)
    if selectedPrinter is None or chosenDevice is None:
        log.warning("No device selected return to main menu")

    # linkPrinterandFilament {{{
    elif devType.lower() == "filament":

        log.info("Linking PRINTER : {0} FILAMENT : {1}".format(
            selectedPrinter.name, chosenDevice.name))
        selectedPrinter.filament = chosenDevice
        chosenDevice.printer = selectedPrinter
        # }}}

    # linkPrinterandCamera {{{
    else:
        log.info("Linking PRINTER : {0} CAMERA : {1}".format(
            selectedPrinter.name, chosenDevice.name))
        selectedPrinter.camera = chosenDevice
        chosenDevice.printer = selectedPrinter
        # }}}

# }}}


# itemSelectionMenu {{{
def itemSelectionMenu(itemList, type):
    choice = None
    while True:
        while choice != len(itemList)+1:  # as long as user doesnt quit
            for i in range(len(itemList)):
                print("{0}. {1}".format(i+1, itemList[i].name))
            print("{}. Quit".format(i+2))  # print quit

            choice = int(input("Select the choice number : "))
            if 0 < choice <= len(itemList):  # if the user selects a device
                selectedItem = itemList[choice-1]
                log.info("{} to be linked.".format(selectedItem.name))
                return selectedItem
            elif choice == len(itemList)+1:
                log.info("No item selected")
                return None
            else:
                print("This is not a valid selection")
# }}}


# Edit Properties {{{
# editPropertiesMenu {{{
def editPropertiesMenu(mainList):
    choice = None

    while choice != 4:

        # Prompt{{{
        print("What would you like to alter?\n"
              "1. Printer\n"
              "2. Filament\n"
              "3. Camera\n")
        # }}}

        choice = int(input('What would you like to do : '))
        if choice == 1:
            log.info("Editing printer")
            editPrinter(itemSelectionMenu(mainList[0], "Printer"))
        elif choice == 2:
            log.info("Editing filament spool")
            editFilament(itemSelectionMenu(mainList[1], "Filament"))
        elif choice == 3:
            log.info("Editing camera")
            editCamera(itemSelectionMenu(mainList[2], "Camera"))
        elif choice == 4:
            log.info("Returning to main menu")
            return

# }}}


# editPrinter {{{
def editPrinter(printer):
    while choice != 6:
        print("What property would you like to edit?\n"
              "1. Name -> {0}\n"
              "2. Model -> {1]}\n"
              "3. Build Volume -> {2}\n"
              "4. Nozzle Diameter -> {3}\n"
              "5. Heated Build Plate -> {4}"
              "6. Quit".format(printer.name,
                               printer.model,
                               printer.bldVolume,
                               printer.nozDiam,
                               printer.heatBldPlt))

        choice = int(input('What would you like to change : '))
        if choice == 1:
            log.info("Editing PRINTER {} name".format(printer.name))
            printer.name = input("New name : ")
        elif choice == 2:
            log.info("Editing PRINTER {} model".format(printer.name))
            printer.model = input("New model : ")
        elif choice == 3:
            log.info("Editing PRINTER {} bldVolume".format(printer.name))
            xVolume = int(input("X build volume : "))
            yVolume = int(input("Y build volume : "))
            zVolume = int(input("Z build volume : "))
            printer.bldVolume = [xVolume, yVolume, zVolume]
        elif choice == 4:
            log.info("Editing PRINTER {} nozDiam".format(printer.name))
            printer.nozDiam = float(input("New nozzle diameter in mm : "))
        elif choice == 5:
            log.info("Editing PRINTER {} heatBldPlt".format(printer.name))
            while choice not in ('y', 'Y', 'n', 'N'):
                choice = input('Is your build plate heated y/n : ')
                if choice == 'y' or choice == 'Y':  # Use currently generated reports
                    heatBldPlt = True
                elif choice == 'n' or choice == 'N':  # Generate new reports
                    heatBldPlt = False
                else:
                    print('This is not a valid selection')
        elif choice == 6:
            print("Quiting")
            log.info("Returning to selection menu.")
        else:
            print("Not a valid selection")
# }}}


# editFilament {{{
def editFilament(fil):
    choice = None
    while choice != 8:

        # Prompt {{{
        print("What property would you like to edit?\n"
              "1. Name -> {0}\n"
              "2. Maker -> {1]}\n"
              "3. Type -> {2}\n"
              "4. Material Diameter-> {3}\n"
              "5. Density -> {4}"
              "6. Remaining Filament -> {5}"
              "7. Colour -> {6}"
              "8. Quit".format(fil.name,
                               fil.company,
                               fil.mat,
                               fil.matDia,
                               fil.density,
                               fil.remFil,
                               fil.colour))

        # }}}

        # Options {{{
        choice = int(input('What would you like to change : '))
        if choice == 1:
            log.info("Editing FILAMENT {} name".format(fil.name))
            fil.name = input("New name : ")
        elif choice == 2:
            log.info("Editing FILAMENT {} maker".format(fil.name))
            fil.company = input("New maker : ")
        elif choice == 3:
            log.info("Editing FILAMENT {} material type".format(fil.name))
            fil.mat = input("New material type : ")
        elif choice == 4:
            log.info("Editing FILAMENT {} material diameter".format(fil.name))
            fil.matDia = float(input("New material diameter in mm : "))
        elif choice == 5:
            log.info("Editing FILAMENT {} material density".format(fil.name))
            fil.density = float(input("New material density in g/cm^3 : "))
        elif choice == 6:
            log.info("Editing FILAMENT {} remaining filament".format(fil.name))
            fil.remFil = int(input("New remaining filament in g : "))
        elif choice == 7:
            log.info("Editing FILAMENT {} colour".format(fil.name))
            fil.colour = input("New colour : ")
        elif choice == 8:
            print("Quiting")
            log.info("Returning to selection menu.")
        else:
            print("Not a valid selection")
# }}}

# }}}


# editCamera {{{
def editCamera(cam):
    choice = None
    while choice != 4:

        # Prompt {{{
        print("What property would you like to edit?\n"
              "1. Name -> {0}\n"
              "2. Model -> {1]}\n"
              "3. Resolution -> {2}\n"
              "4. Quit".format(cam.name,
                               cam.model,
                               cam.resolution))

        # }}}

        # Choices {{{
        choice = int(input('What would you like to change : '))
        if choice == 1:
            log.info("Editing CAMERA {} name".format(cam.name))
            cam.name = input("New name : ")
        elif choice == 2:
            log.info("Editing CAMERA {} model".format(cam.name))
            cam.name = input("New maker : ")
        elif choice == 3:
            log.info("Editing CAMERA {} resolution".format(cam.name))
            xRes = int(input("X resolution : "))
            yRes = int(input("Y resolution : "))
            cam.resolution = [xRes, YRes]
        elif choice == 4:
            print("Quiting")
            log.info("Returning to selection menu.")
        else:
            print("Not a valid selection")
        # }}}
# }}}

# }}}
