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
    name = input("What is the name of this camera : ")
    model = input("What model of camera is this : ")
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

    while choice != 7:
        # Prompt {{{
        print("\n\nAutomata3d : Printer Management Software\n\n\n"
              "Please select the number next to the option you would like\n\n"
              "1. Begin print job\n"
              "2. View printer status\n"
              "3. Access filament library\n"
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
                print("Access filament library")
            elif choice == 4:
                print("View cameras")
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
        log.warning("There are no {} created yet.".format(devType))
        return
    while choice != len(devList)+1:  # as long as user doesnt quit
        print("What {} would you like to remove:".format(devType))
        for i in range(len(devList)):  # print entire dev list
            print("{0}. {1}".format(i+1, devList[i]))
        print("{}. Quit".format(i+2))  # print quit
        choice = int(input("Select the number of the device  to remove : "))
        if 0 < choice <= len(devList):  # if the user selects a device
            if confirmationPrompt():  # Confirm the user chioce
                log.info("Removing {}".format(devList[choice-1].name))
                del devList[choice-1]  # Delete the device
            else:
                log.info("Choice canceled")
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
    while choice != len(mainList[0])+1:  # as long as user doesnt quit

        # Prompt {{{
        print("What Printer would you like to view.")
        for i in range(len(mainList[0])):  # print entire dev list
            if mainList[0][i].camera is None:  # Check if camera conncted
                print("{0}. {1} (No camera)".format(i+1, mainList[0][i].name))
            else:
                print("{0}. {1}".format(i+1, mainList[0][i].name))
        print("{}. Quit".format(i+2))  # print quit
        # }}}

        choice = int(input("Select the number of the Printer to view : "))
        if 0 < choice <= len(mainList[0]):  # if the user selects a device
            mainList[0][choice-1].camera.showVideoStream()
        elif choice == len(mainList[0])+1:
            log.info("Returning to camera menu")
            return
        else:
            print("This is not a valid selection")
            # }}}


# linkMenu {{{
def linkMenu(printers, devices, devType):
    choice = None
    while True:

        # Printer selection {{{
        while choice != len(printers)+1:  # as long as user doesnt quit

            # Prompt {{{
            print("What Printer would you like to link.")
            for i in range(len(printers)):  # print entire dev list
                print("{0}. {1}".format(i+1, printers[i].name))
            print("{}. Quit".format(i+2))  # print quit
            # }}}

            choice = int(input("Select the number of the Printer to link : "))
            if 0 < choice <= len(printers):  # if the user selects a device
                selectedPrinter = printers[choice-1]
                log.info("{} to be linked.".format(selectedPrinter.name))
                break
            elif choice == len(printers)+1:
                log.info("Returning to link menu")
                return
            else:
                print("This is not a valid selection")
                # }}}

        # Device selection {{{
        while choice != len(devices)+1:  # as long as user doesnt quit

            # Prompt {{{
            print("What {} would you like to link.".format(devType))
            for i in range(len(devices)):  # print entire dev list
                print("{0}. {1}".format(i+1, devices[i].name))
            print("{}. Quit".format(i+2))  # print quit
            # }}}

            choice = int(
                input("Select the number of {} to link : ".format(devType)))
            if 0 < choice <= len(devices):  # if the user selects a device
                chosenDevice = devices[choice-1]
                log.info("{} to be linked.".format(chosenDevice.name))
                break
            elif choice == len(devices)+1:
                log.info("Returning to link menu")
                return
            else:
                print("This is not a valid selection")
                # }}}

        # linkPrinterandFilament {{{
        if devType.lower() == "filament":

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
