from statistics import mean
import numpy as np
import cv2
import time

# Instructions {{{
"""
TODO:

difImages
Get 3 images and compare them. If there are big changes horizontally than there is likely a print failure

hsvSelection
Add the ability to select the print material from the image and use HSV to hide the background.

blob detection
The biggest object of the same colour in the frame is selected as the main object.
If there are too many changes from the center of the box than abort because it detached

Compare the top of the box bounding box against the position of the nozzle to determine if the filament ran out.

Need to add parallax calculations to the machine vision algorithm that way we can print in 3 dimensions.
"""

# }}}

# getCircles {{{
def getCircles(image, circleType):
    if circleType == "bed":
        circles = cv2.HoughCircles(image,
                                   cv2.HOUGH_GRADIENT,
                                   1,  # Type of detection
                                   500,  # Distance between points
                                   param1=60,  # Canny threshold
                                   param2=4,  # Base detection
                                   minRadius=6,  # min rad
                                   maxRadius=10)  # max rad

    if circleType == "nozzle":
        circles = cv2.HoughCircles(image,
                                   cv2.HOUGH_GRADIENT,
                                   1,  # Type of detection
                                   50,  # Distance between points
                                   param1=130,  # Canny threshold
                                   param2=12,  # Base detection
                                   minRadius=6,  # min rad
                                   maxRadius=10)  # max rad

    return circles
#}}}

# getAverageCircles {{{
def getAverageCircles(frameList, markerType, markers=2):

    #Setup
    averageList = [[] for x in range(markers)]
    returnList = []

    # iterate thourgh frames {{{
    for frame in frameList:
        circles = getCircles(frame, markerType)

        if circles is not None: #If there are circles
            circles = np.int16(np.around(circles))
            circles = circles[0] #Remove the one dimensional list
            if len(circles) == markers: #If we find the right number of circles
                circles = sorted(circles, key=lambda x:x[:][0]) #Sort circles by x
                for i in range(markers):
                    averageList[i].append(circles[i])

    # }}}

    if len(averageList[0]) > 1:

        # convert to list {{{
        for i in range(len(averageList)):
            tempList = np.mean(averageList[i], axis=0) #Get the average of the list
            returnList.append(tempList.tolist())
        # }}}

        # try to round to int {{{
        try:
            for i in range(len(returnList)):
                for j in range(len(returnList[i])):
                    returnList[i][j] = int(returnList[i][j]) #Convert all values to int
            return returnList
        except TypeError:
            return
        # }}}
# }}}

# cropImage {{{
def cropImage(image, bedMarkers=None, nozzleMarkers=None):
    if bedMarkers and nozzleMarkers is None:
        markers = bedMarkers
        xMin = min(map(lambda x: x[0], markers))
        xMax = max(map(lambda x: x[0], markers))

        yMin = min(map(lambda x: x[1], markers))
        yMax = max(map(lambda x: x[1], markers))
        return image[:yMax-30, xMin:xMax], [0, yMax-30, xMin, xMax]

    if bedMarkers and nozzleMarkers:
        markers = []
        for marker in bedMarkers:
            markers.append(marker)
        for marker in nozzleMarkers:
            markers.append(marker)


        yMin = min(map(lambda x: x[0], markers))
        yMax = max(map(lambda x: x[0], markers))

        xMin = min(map(lambda x: x[1], markers))
        xMax = max(map(lambda x: x[1], markers))
        return image[xMin:xMax, yMin:yMax],  [yMin, yMax, xMin, xMax]

# }}}

# locPrintHead {{{
def locPrintHead(nozMarkers):
    x = int((nozMarkers[1][0] - nozMarkers[0][0]) / 2 + nozMarkers[0][0] - 30)
    y = int(nozMarkers[0][1] + 30)
    z = 0
    return [x, y, z]
#}}}

# markerImage {{{
def markerImage(image):
    bedMakers = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    nozzleMarkers = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    bedLower, bedUpper, nozzleLower, nozzleUpper = getHsvValues()
    bedMask = cv2.inRange(bedMakers, bedLower, bedUpper)
    nozzleMask = cv2.inRange(nozzleMarkers, nozzleLower, nozzleUpper)
    return bedMask, nozzleMask
#}}}

# getHsvValues {{{
def getHsvValues():
    #values = input("Please input the RGB value seperated by a space : ")
    values = "130 200 107"
    valueList = values.split()
    for i in range(len(valueList)):
        valueList[i] = int(valueList[i])
    BGRValues = np.uint8([[valueList]])
    hsv_values = cv2.cvtColor(BGRValues, cv2.COLOR_RGB2HSV)

    bedLower = hsv_values.copy()
    bedUpper = hsv_values.copy()

    nozzleLower = hsv_values.copy()
    nozzleUpper = hsv_values.copy()

    bedLower[0][0][0] = 150
    bedLower[0][0][1] = 200
    bedLower[0][0][2] = 200

    bedUpper[0][0][0] = 255
    bedUpper[0][0][1] = 255
    bedUpper[0][0][2] = 255

    nozzleLower[0][0][0] = 45
    nozzleLower[0][0][1] = 25
    nozzleLower[0][0][2] = 25

    nozzleUpper[0][0][0] = 255
    nozzleUpper[0][0][1] = 255
    nozzleUpper[0][0][2] = 255

    return bedLower, bedUpper, nozzleLower, nozzleUpper
# }}}

# findCircles {{{
def findCircles(frameList, markerImage, markerType, averageValue=10):
    averagedMarkers = None
    if len(frameList) > averageValue:
        averagedMarkers = getAverageCircles(frameList, markerType)
        del frameList[0]
    if averagedMarkers is not None:
        return averagedMarkers
# }}}

# drawCircles {{{
def drawCircles(image, bedMarkers=None, nozzleMarkers=None, printHead=None):
    if bedMarkers is not None:
        for circle in bedMarkers:
            cv2.circle(image, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
            cv2.circle(image, (circle[0], circle[1]), 2, (0, 0, 255), 2)
    if nozzleMarkers is not None:
        for circle in nozzleMarkers:
            cv2.circle(image, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
            cv2.circle(image, (circle[0], circle[1]), 2, (0, 0, 255), 2)
    if printHead is not None:
        cv2.circle(output, (printHead[0], printHead[1]), 3, (255, 0, 0), 2)
    return image

#}}}


if __name__ == '__main__':

    # setup {{{
    cap = cv2.VideoCapture("/dev/Cameras/MachineVision")
    bedFrames = []
    nozzleFrames = []
    averagedListValues = None
    avgBed = None
    avgNozzle = None

    # }}}

    while True:

        # getImage {{{
        ret, image = cap.read()
        image = cv2.flip(image, 0)
        output = image.copy()
        output2 = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        bedMask, nozzleMask = markerImage(image)
        bedImage = cv2.GaussianBlur(bedMask, (5, 5), 0)
        nozzleImage = cv2.GaussianBlur(nozzleMask, (5, 5), 0)
        # }}}

        bedFrames.append(bedImage)
        nozzleFrames.append(nozzleImage)
        avgBed = None
        avgNozzle = None
        printHead = None
        avgBed = findCircles(bedFrames, bedImage, "bed")
        if avgBed:
            nozzleOutput, s = cropImage(nozzleImage, bedMarkers=avgBed)
            avgNozzle = findCircles(nozzleFrames, nozzleOutput, "nozzle")
            kernel = np.ones((10,10),np.uint8)
            opening = cv2.morphologyEx(nozzleOutput, cv2.MORPH_OPEN, kernel)
            avgNozzle = getCircles(nozzleOutput, "nozzle")
            nozzleOutput = output[s[0]:s[1], s[2]:s[3]]
            nozzleOutput = cv2.bitwise_and(nozzleOutput, nozzleOutput, mask=nozzleMask[s[0]:s[1], s[2]:s[3]])
            try:
                avgNozzle = avgNozzle[0]
            except TypeError:
                pass
            if len(avgNozzle) != 2:
                print(len(avgNozzle))
                drawCircles(nozzleOutput, avgBed, avgNozzle, printHead)
                cv2.imshow("output", nozzleOutput)
                cv2.waitKey(0)
        #if avgNozzle:
            #processingImage = cropImage(output, bedMarkers=avgBed, nozzleMarkers=avgNozzle)
            #printHead = locPrintHead(avgNozzle)
        else:
            print("failed")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
