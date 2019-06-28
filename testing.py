import serial

serial.Serial("/dev/Printers.tyUSB0", 115200)
grbl_out = self.serial.readline()
print(' : ' + str(grbl_out.strip()))
