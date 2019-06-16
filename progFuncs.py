# Imports {{{
import logging as log
import os
import sys
from filamentClass import Filament
from printerClass import Printer
from cameraClass import Camera
from datetime import datetime
import pickle
from tkinter.filedialog import askopenfilename
# }}}


# inWrap {{{
def inWrap(message, inType=str, numCheck=None):
    while True:
        try:
            userInput = (inType(input(message)))
            if numCheck is not None:
                if userInput < 1 or userInput > numCheck:
                    raise ValueError
            return userInput
        except ValueError:
            log.warning("Invalid selection. Input should be a {}".format(inType.__name__))
# }}}


# Create Devices {{{


# createPrinter {{{
def createPrinter(printerList):
    choice = None

    # Prompt {{{
    name = inWrap("What is the name of this printer : ")
    model = inWrap("What model of printer is this : ")
    print("Please enter your build volume in the order of X, Y, Z")
    xVolume = inWrap("What is the build volume of your printer (X) : ", int)
    yVolume = inWrap("What is the build volume of your printer (Y) : ", int)
    zVolume = inWrap("What is the build volume of your printer (Z) : ", int)
    bldVolume = [xVolume, yVolume, zVolume]
    nozDiam = inWrap("What is your nozzle diameter in mm : ", float)
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
             "Model -> " + model + "\n"
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
    with open(Filament.filamentTypeFile, "r+") as f:
        typeList = f.readlines()
    with open(Filament.filamentColourFile, "r+") as f:
        colourList = f.readlines()

    # Prompt {{{
    name = inWrap("What is the name of this filament : ")
    company = inWrap("Who makes this filament : ")
    print("What type of material is this filament")
    mat = itemSelectionMenu(typeList, Filament.filamentTypeFile)
    matDia = inWrap("What is the diameter of this filament in mm : ", float)
    dense = inWrap("What is the density of the filament in g/cm^3 : ", float)
    weight = inWrap("What is the weight of this filament in g : ", int)
    print("What colour is this filament")
    colour = itemSelectionMenu(colourList, Filament.filamentColourFile)
    # }}}

    # logFile {{{
    log.info("A filament with the following properties has been added:\n"
             "Name -> " + name + "\n"
             "Company -> " + company + "\n"
             "Material -> " + mat + "\n"
             "Material diameter -> " + str(matDia) + "mm\n"
             "Density -> " + str(dense) + "g/cm^3\n"
             "Weight -> " + str(weight) + "g\n"
             "Colour -> " + colour + "\n")
    # }}}

    instance = Filament(name, company, mat, matDia, dense, weight, colour)
    filamentList.append(instance)

# }}}


# createCamera {{{
def createCamera(cameraList):

    # Prompt {{{
    name = inWrap("What is the name of this camera : ")
    model = inWrap("What model of camera is this : ")
    xRes = inWrap("X resolution : ", int)
    yRes = inWrap("Y resolution : ", int)
    resolution = [xRes, yRes]
    # }}}

    # logFile {{{
    log.info("A printer with the following properties has been added:\n"
             "Name -> " + name + "\n"
             "Model -> " + model + "\n"
             "Resolution -> " + 'x'.join(str(e) for e in resolution) + "\n")

    # }}}

    instance = Camera(name, model, resolution)
    cameraList.append(instance)

# }}}


# addDeviceMenu {{{
def addDeviceMenu(databaseFile, mainList):

    while True:

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

        choice = inWrap('What would you like to do : ', int, 6)
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


# linkMenu {{{
def linkMenu(printers, devices, devType):
    print("What Printer would you like to link.")
    selectedPrinter = itemSelectionMenu(printers)
    if selectedPrinter is None:
        log.warning("No Printer selected return to add device menu")
        return
    print("What {} would you like to link.".format(devType))
    chosenDevice = itemSelectionMenu(devices)
    if chosenDevice is None:
        log.warning("No {} selected. Leaving link menu".format(devType))
        return

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

# }}}


# changeToRoot {{{
def toggleRoot():
    if os.geteuid() != 0:
        log.info("Resigning in as sudo")
        os.execvp("sudo", ["sudo", "python3"] + sys.argv)
    if os.geteuid() == 0:
        sudoID = int(os.getenv("SUDO_UID"))
        os.seteuid(sudoID)
        os.execvp("python3", ["python3"] + sys.argv)
        log.info("Resigning in as regular user")
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


# addFile {{{
def addFile(databaseFile, mainList):

    # Setup {{{
    with open(Filament.filamentTypeFile, "r+") as f:
        typeList = f.readlines()
    with open(Filament.filamentColourFile, "r+") as f:
        colourList = f.readlines()
    propMat = []
    finalOptions = []
    # }}}

    # User Input {{{
    print("Please select your print")
    newFile = askopenfilename()
    print("Please select your material type and colour.\n"
          "If you do not see your choice here it is because there is no filament that exists with those attributes.\n")
    # }}}

    # Check Material Type {{{
    while True:
        print("What type of material is your print")
        matType = itemSelectionMenu(typeList, "Filament")
        if matType is None:
            log.warning("File addition canceled")
            return
        for i in range(len(mainList[0])):
            try:
                if mainList[0][i].filament.mat == matType:
                    propMat.append(mainList[0][i])
            except AttributeError:
                log.warning("PRINTER : {} is not linked to a filament.".format(mainList[0][i].name))
        if len(propMat) == 0:
            log.warning("No printer found with spool of type {}. Please link and add this filament to printer.".format(matType))
        else:
            break

        # }}}

    # Check Material Colour {{{
    while True:
        print('What colour is your print')
        matColour = itemSelectionMenu(colourList, "Filament")
        if matColour is None:
            log.warning("File addition canceled")
            return
        for i in range(len(mainList[0])):
            if mainList[0][i].filament.colour == matColour:
                finalOptions.append(mainList[0][i])
        if len(finalOptions) == 0:
            log.warning("No {0} {1} filament is currently loaded.".format(matType, matColour))
        else:
            break

        # }}}

    printer = itemSelectionMenu(finalOptions, "Queue")
    if printer is not None:
        print(newFile.split("/")[-1].split(".")[0])
        printer.addToQueue(newFile.split("/")[-1].split(".")[0], newFile)

        with open(databaseFile, "wb") as f:
            pickle.dump(mainList, f)
        return
    else:
        log.warning("File addition canceled")
        return
#}}}


# mainMenu{{{
def mainMenu(databaseFile):

    # Initialization {{{
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M")
    log.info('New session started : {}'.format(currentTime))
    mainList = checkDatabase(databaseFile)
    print(mainList)
    # }}}

    while True:
        # Prompt {{{
        print("\n\nAutomata3d : Printer Management Software\n\n\n"
              "Please select the number next to the option you would like\n\n"
              "1. Start prints\n"
              "2. Add print job\n"
              "3. View printer status\n"
              "4. Edit properties\n"
              "5. View cameras\n"
              "6. Add a new printer / filament / camera\n"
              "7. Remove printer / filament / camera\n"
              "8. Toggle root status\n"
              "9. Exit\n")
        # }}}

        choice = inWrap('What would you like to do : ', int, 9)
        if choice == 1:
            for i in range(len(mainList[0])):
                if not mainList[0][i].jobStart and mainList[0][i].bedClear:
                    log.info("Starting Printer {}".format(mainList[0][i].name))
                    mainList[0][i].recordToSD()
        elif choice == 2:
            if os.geteuid() !=0:
                log.warning("You must be root to add files. Escalating permissions.")
                toggleRoot()
            log.info("Adding file")
            addFile(databaseFile, mainList)
        elif choice == 3:
            log.info("Viewing status")
            viewPrinterMenu(mainList)
        elif choice == 4:
            if os.geteuid() !=0:
                log.warning("Cannot edit devices as non root user. Escalating permissions.")
                toggleRoot()
            log.info("Accessing edit properties menu")
            editPropertiesMenu(databaseFile, mainList)
        elif choice == 5:
            if os.geteuid() ==0:
                log.warning("Cameras not accessible as root. Descalating permssions.")
                toggleRoot()
            log.info("Viewing cameras")
            checkCamerasMenu(mainList)
        elif choice == 6:
            if os.geteuid() !=0:
                log.warning("Cannot create devices as non root user. Escalating permissions.")
                toggleRoot()
            log.info("Accessing device creation menu")
            addDeviceMenu(databaseFile, mainList)
        elif choice == 7:
            if os.geteuid() !=0:
                log.warning("Cannot deletedevices as non root user. Escalating permissions.")
                toggleRoot()
            log.info("Resigning in as sudo")
            deleteMenu(databaseFile, mainList)
        elif choice == 8:
            log.info("Toggling root status")
            toggleRoot()
        elif choice == 9:
            # Close program {{{
            print("Have a great day.")
            with open(databaseFile, "wb") as f:
                pickle.dump(mainList, f)
                currentTime = datetime.now().strftime("%Y-%m-%d %H:%M")
                log.info('Session closed at : {}'.format(currentTime))
                exit()
            # }}}
# }}}


# Delete Devices {{{
# deleteMenu {{{
def deleteMenu(databaseFile, mainList):

    while True:

        # Prompt {{{
        print("\n\nWhat device would you like to remove ?\n\n\n"
              "Please select the number next to the option you would like\n\n"
              "1. Printer\n"
              "2. Filament\n"
              "3. Camera\n"
              "4. Return to main menu\n")
        # }}}

        choice = inWrap('What would you like to do : ', int, 4)
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
    if len(devList) == 0:  # Check if no devices
        log.warning("There are no {}s created yet.".format(devType))
        return
    while True:
        print("What {} would you like to remove:".format(devType))
        chosenDev = itemSelectionMenu(devList)
        if chosenDev is None:
            log.warning("No device chosen returning to delete device menu")
            return
        if confirmationPrompt():  # Confirm the user choice
            log.info("Removing {}".format(chosenDev.name))
            if devType.lower() == "printer" or devType.lower() == "camera":
                delUdev(chosenDev)
            devList.remove(chosenDev)  # Delete the device
        else:
            log.info("Choice canceled")
    # }}}


# delUdev {{{
def delUdev(chosenDev):
    try:
        with open(chosenDev.udevRulesFile, "r+") as f:
            file = f.readlines()
            for line in file:
                if chosenDev.name not in line:
                    f.write(line)
                f.truncate()
    except FileNotFoundError:
        log.warning("No udev file found skipping")

# }}}

# }}}


# confirmationPrompt {{{
def confirmationPrompt():
    choice = None
    while choice not in ("y", "Y", "n", "N"):
        choice = inWrap("Please confirm your selection (y/n) : ")
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

    if len(mainList[0]) == 0:  # Check if no devices
        log.warning("There are no Printers created yet.")
        return
    elif len(mainList[2]) == 0:  # Check if no devices
        log.warning("There are no Cameras created yet.")
        return

    while True:
        print("What Printer would you like to view.")
        printer = itemSelectionMenu(mainList[0])
        if printer is None:
            log.warning("No Printer selected quitting")
            return
        elif printer.camera is None:  # Check if camera connected
            log.warning("{} has no camera associated".format(printer.name))
        else:
            printer.camera.showVideoStream()

# }}}


# itemSelectionMenu {{{
def itemSelectionMenu(itemList, specialList=None):
    choice = None
    index = 0

    # NormalList {{{
    if specialList is None:
        while choice != len(itemList)+1:  # as long as user doesnt quit

            # Prompt {{{
            while index != len(itemList):  # print entire dev list
                print("{0}. {1}".format(index+1, itemList[index].name))
                index +=1
            print("{}. Quit".format(index+1))  # print quit
            # }}}

            choice = inWrap("Select the item number: ", int)
            if 0 < choice <= len(itemList):  # if the user selects a device
                selectedItem = itemList[choice-1]
                log.info("{} to be linked.".format(selectedItem.name))
                return selectedItem
            elif choice == len(itemList)+1:
                log.info("Leaving selection menu")
                return
            else:
                print("This is not a valid selection")

                # }}}

    # Printer Queue {{{
    elif specialList == "Queue":
        while choice != len(itemList)+1:  # as long as user doesnt quit

            # Prompt {{{
            while index != len(itemList):  # print entire dev list
                print("{0}. {1} -> {2}".format(index+1, itemList[index].name, len(itemList[index].pQueue)))
                index +=1
            print("{}. Quit".format(index+1))  # print quit
            # }}}

            choice = inWrap("Select the item number: ", int)
            if 0 < choice <= len(itemList):  # if the user selects a device
                selectedItem = itemList[choice-1]
                return selectedItem
            elif choice == len(itemList)+1:
                log.info("Leaving selection menu")
                return
            else:
                print("This is not a valid selection")

                # }}}

    # Filament Select {{{
    elif specialList == "Filament":
        while choice != len(itemList)+1:  # as long as user doesnt quit

            # Prompt {{{
            while index != len(itemList):  # print entire dev list
                print("{0}. {1}".format(index+1, itemList[index]))
                index +=1
            print("{}. Quit".format(index+1))  # print quit
            # }}}

            choice = inWrap("Select the item number: ", int)
            if 0 < choice <= len(itemList):  # if the user selects a device
                selectedItem = itemList[choice-1]
                log.info("{} to be linked.".format(selectedItem))
                return selectedItem
            elif choice == len(itemList)+1:
                log.info("Leaving selection menu")
                return
            else:
                print("This is not a valid selection")

                # }}}

    # Filament Creation {{{
    else:
        while choice != len(itemList)+1:  # as long as user doesnt quit

            # Prompt {{{
            while index != len(itemList):  # print entire dev list
                print("{0}. {1}".format(index+1, itemList[index]))
                index +=1
            print("{}. Custom value".format(index+1))
            print("{}. Quit".format(index+2))  # print quit
            # }}}

            choice = inWrap("Select the item number: ", int)
            if 0 < choice <= len(itemList):  # if the user selects a device
                selectedItem = itemList[choice-1]
                log.info("{} to be selected.".format(selectedItem))
                return selectedItem
            elif choice == len(itemList)+1:
                selectedItem = inWrap("What is the name of your new entry : ")
                log.info("New filament entry added : {}.".format(selectedItem))
                with open(specialList, "a+") as f:
                    f.write(selectedItem)
                return selectedItem
            elif choice == len(itemList)+2:
                log.info("Leaving selection menu")
                return
            else:
                print("This is not a valid selection")

                # }}}

# }}}


# Edit Properties {{{


# editPropertiesMenu {{{
def editPropertiesMenu(databaseFile, mainList):
    while True:

        # Prompt {{{
        print("\n\nWhat device type would you like to edit ?\n\n\n"
              "1. Printer\n"
              "2. Filament\n"
              "3. Camera\n"
              "4. Return to main menu\n")
        # }}}

        choice = inWrap('What would you like to do : ', int, 4)
        if choice == 1:
            log.info("Editing printer")
            saveChanges = editPrinter(mainList[0])
        if choice == 2:
            log.info("Editing filament spool")
            saveChanges = editFilament(mainList[1])
        if choice == 3:
            log.info("Editing camera")
            saveChanges = editCamera(mainList[2])
        if choice == 4:
            log.info("Returning to main menu")
            return
        if saveChanges:
            with open(databaseFile, "wb") as f:
                pickle.dump(mainList, f)

# }}}


# editPrinter {{{
def editPrinter(printerList):

    # Check if no printers {{{
    if len(printerList) == 0:  # Check if no devices
        log.warning("There are no Printers created yet.")
        return
    # }}}

    while True:

        # Select printer {{{
        prn = itemSelectionMenu(printerList)
        if prn is None:
            log.warning(
                "No printer chosen returning to edit properties menu")
            return
        log.info("PRINTER : {} selected to modify".format(prn.name))
        # }}}

        bldVStr = 'x'.join(str(e) for e in prn.bldVolume)
        while True:

            # Prompt {{{
            print("1. Name -> " + prn.name + "\n"
                  "2. Model -> " + prn.model + "\n"
                  "3. Build volume -> " + bldVStr + "\n"
                  "4. Nozzle diameter -> " + str(prn.nozDiam) + "\n"
                  "5. Heated build plate -> " + str(prn.heatBldPlt) + "\n"
                  "6. Quit")
            # }}}

            choice = inWrap("What property to modify : ", int, 6)
            if choice == 1:
                oldName = prn.name
                prn.name = inWrap("Name : {} -> ".format(prn.name))
                log.info("{0} name changed to {1}".format(oldName, prn.name))
            if choice == 2:
                prn.model = inWrap("Model : {} -> ".format(prn.model))
                log.info("{0} model changed to {1}".format(
                    prn.name, prn.model))
            if choice == 3:
                print(bldVStr)
                xSize = inWrap("X build size in mm : ", int)
                ySize = inWrap("Y build size in mm : ", int)
                zSize = inWrap("Z build size in mm : ", int)
                prn.bldVolume = [xSize, ySize, zSize]
                bldVStr = 'x'.join(str(e) for e in prn.bldVolume)
                log.info("{0} build size changed to {1}".format(
                    prn.name, bldVStr))
            if choice == 4:
                prn.nozDiam = inWrap("Name : {} -> ".format(prn.name), float)
                log.info("{0} nozzle diameter changed to {1}".format(
                    prn.name, prn.nozDiam))
            if choice == 5:
                while choice not in ('y', 'Y', 'n', 'N'):
                    choice = input('Is your build plate heated y/n : ')
                    if choice == 'y' or choice == 'Y':  # Use currently generated reports
                        prn.heatBldPlt = True
                    elif choice == 'n' or choice == 'N':  # Generate new reports
                        prn.heatBldPlt = False
                    else:
                        print('This is not a valid selection')
                log.info("{0} heated bed changed to {1}".format(
                    prn.name, prn.heatBldPlt))
            if choice == 6:
                print("Are all changes complete")
                if confirmationPrompt():
                    print("Would you like to save your changes")
                    if confirmationPrompt():
                        log.info("Saving changes and returning to edit properties screen")
                        return True
                    else:
                        log.warning("Changes not saved")
                        return False


# }}}


# editFilament {{{
def editFilament(filamentList):

    with open(Filament.filamentTypeFile, "r+") as f:
        typeList = f.readlines()
    with open(Filament.filamentColourFile, "r+") as f:
        colourList = f.readlines()

    # Check if no filaments {{{
    if len(filamentList) == 0:  # Check if no devices
        log.warning("There are no Filaments created yet.")
        return
    # }}}

    while True:

        # Select filament {{{
        fil = itemSelectionMenu(filamentList)
        if fil is None:
            log.warning(
                "No filament chosen returning to edit properties menu")
            return
        log.info("FILAMENT : {} selected to modify".format(fil.name))
        # }}}

        while True:

            # Prompt {{{
            print("1. Name -> " + fil.name + "\n"
                  "2. Company -> " + fil.company + "\n"
                  "3. Material -> " + fil.mat + "\n"
                  "4. Material diameter -> " + str(fil.matDia) + "mm\n"
                  "5. Density -> " + str(fil.density) + "g/cm^3\n"
                  "6. Remaining Filament -> " + str(fil.remFil) + "g\n"
                  "7. Colour -> " + str(fil.colour) + "\n"
                  "8. Quit")
            # }}}

            choice = inWrap("What property to modify : ", int, 8)
            if choice == 1:
                oldName = fil.name
                fil.name = inWrap("Name : {} -> ".format(fil.name))
                log.info("{0} name changed to {1}".format(oldName, fil.name))
            if choice == 2:
                fil.company = inWrap("Maker : {} -> ".format(fil.company))
                log.info("{0} maker changed to {1}".format(fil.name, fil.company))
            if choice == 3:
                fil.mat = itemSelectionMenu(typeList, Filament.filamentTypeFile)
                log.info("{0} material changed to {1}".format(fil.name, fil.mat))
            if choice == 4:
                fil.matDia = inWrap("Material diameter : {} -> ".format(fil.matDia), float)
                log.info("{0} material diamter changed to {1}".format(fil.name, fil.matDia))
            if choice == 5:
                fil.density = inWrap("Density : {} -> ".format(fil.density), float)
                log.info("{0} density changed to {1}".format(fil.name, fil.density))
            if choice == 6:
                fil.remFil = inWrap("Remaining filament : {}g -> ".format(fil.remFil), int)
                log.info("{0} remaining filament changed to {1}".format(fil.name, fil.remFil))
            if choice == 7:
                fil.colour = itemSelectionMenu(colourList, Filament.filamentColourFile)
                log.info("{0} colour changed to {1}".format(fil.name, fil.colour))
            if choice == 8:
                print("Are all changes complete")
                if confirmationPrompt():
                    print("Would you like to save your changes")
                    if confirmationPrompt():
                        log.info("Saving changes and returning to edit properties screen")
                        return True
                    else:
                        log.warning("Changes not saved")
                        return False

# }}}


# editCamera {{{
def editCamera(cameraList):

    # Check if no printers {{{
    if len(cameraList) == 0:  # Check if no devices
        log.warning("There are no Cameras created yet.")
        return
    # }}}

    while True:

        # Select camera {{{
        cam = itemSelectionMenu(cameraList)
        if cam is None:
            log.warning("No camera chosen returning to edit properties menu")
            return
        log.info("CAMERA : {} selected to modify".format(cam.name))
        # }}}

        res = 'x'.join(str(e) for e in cam.resolution)
        while True:

            # Prompt {{{
            print("1. Name -> " + cam.name + "\n"
                  "2. Model -> " + cam.model + "\n"
                  "3. Resolution -> " + res + "\n"
                  "4. Quit")
            # }}}

            choice = inWrap("What property to modify : ", int, 4)
            if choice == 1:
                oldName = cam.name
                cam.name = inWrap("Name : {} -> ".format(cam.name))
                log.info("{0} name changed to {1}".format(oldName, cam.name))
            if choice == 2:
                cam.model = inWrap("Model : {} -> ".format(cam.model))
                log.info("{0} model changed to {1}".format(
                    cam.name, cam.model))
            if choice == 3:
                xRes = inWrap("X resolution : ", int)
                yRes = inWrap("Y resolution : ", int)
                cam.resolution = [xRes, yRes]
                res = 'x'.join(str(e) for e in cam.resolution)
                log.info("{0} resolution changed to {1}".format(cam.name, res))
            if choice == 4:
                print("Are all changes complete")
                if confirmationPrompt():
                    print("Would you like to save your changes")
                    if confirmationPrompt():
                        log.info("Saving changes and returning to edit properties screen")
                        return True
                    else:
                        log.warning("Changes not saved")
                        return False

# }}}

# }}}


# viewPrinterMenu {{{
def viewPrinterMenu(mainList):
    while True:

        # Prompt {{{
        print("\n\nWhat would you like to do?\n\n\n"
              "1. View printer status\n"
              "2. Send commands\n"
              "3. Return to main menu\n")
        # }}}

        choice = inWrap('What would you like to do : ', int, 3)
        if choice == 1:
            printer = itemSelectionMenu(mainList[0])
            log.info("Editing PRINTER {}".format(printer.name))
            printer.printInfo()
        if choice == 2:
            printer = itemSelectionMenu(mainList[0])
            log.info("Sending commands to printer {}".format(printer.name))
            printer.sendCommands()
            saveChanges = editFilament(mainList[1])
        if choice == 3:
            log.info("Returning to main menu")
            return

# }}}
