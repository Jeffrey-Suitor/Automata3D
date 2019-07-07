from statistics import mean
import numpy as np
import cv2
import time
import itertools
import logging as log

# Logger {{{
log.basicConfig(level=log.INFO)
logger = log.getLogger(__name__)
#}}}

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
        if circles is None:
            log.debug("No circles nozzle markers found")

    if circleType == "nozzle":
        circles = cv2.HoughCircles(image,
                                   cv2.HOUGH_GRADIENT,
                                   1,  # Type of detection
                                   100,  # Distance between points
                                   param1=130,  # Canny threshold
                                   param2=12,  # Base detection
                                   minRadius=6,  # min rad
                                   maxRadius=10)  # max rad
        if circles is None:
            log.debug("No circles nozzle markers found")
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

        if circles is not None:  # If there are circles
            circles = np.int16(np.around(circles))
            circles = circles[0]  # Remove the one dimensional list
            circles = sorted(circles, key=lambda x:x[:][0])  # Sort circles by x
            if len(circles) == markers:  # If we find the right number of circles
                if abs(circles[0][1] - circles[1][1]) < 15 and abs(circles[0][0] - circles[1][0]) > 100:
                    averageList[0].append(circles[0])
                    averageList[1].append(circles[1])

            elif len(circles) > markers:
                for c1, c2, in itertools.product(circles, circles):
                    if abs(c1[1] - c2[1]) < 15 and abs(c1[0] - c2[0]) > 100 and c1[0] != c2[0]:
                        averageList[0].append(c1)
                        averageList[1].append(c2)
                        break

    # }}}

    if len(averageList[0]) > 1:

        # convert to list {{{
        for i in range(len(averageList)):
            tempList = np.mean(averageList[i], axis=0)  # Get the average of the list
            returnList.append(tempList.tolist())
        # }}}

        # try to round to int {{{
        try:
            for i in range(len(returnList)):
                for j in range(len(returnList[i])):
                    returnList[i][j] = int(returnList[i][j])  # Convert all values to int
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
        return image[:yMax-30, :]

    if bedMarkers and nozzleMarkers:
        markers = []
        for marker in bedMarkers:
            markers.append(marker)
        for marker in nozzleMarkers:
            markers.append(marker)


        xMin = min(map(lambda x: x[0], markers))
        xMax = max(map(lambda x: x[0], markers))

        yMin = min(map(lambda x: x[1], markers))
        yMax = max(map(lambda x: x[1], markers))
        return image[yMin:yMax, xMin:xMax]

# }}}

# locPrintHead {{{
def locPrintHead(nozMarkers):
    x = int((nozMarkers[1][0] - nozMarkers[0][0]) / 2 + nozMarkers[0][0] - 17)
    y = int(nozMarkers[0][1] + 25)
    z = 0
    return [x, y, z]
#}}}

# markerImage {{{
def markerImage(image):
    bedMrk = nozMrk = prtMrk = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    bedL, bedU, nozL, nozU, prtL, prtU = getHsvValues()

    bedMask = cv2.inRange(bedMrk, bedL, bedU)
    nozzleMask = cv2.inRange(nozMrk, nozL, nozU)
    partMask = cv2.inRange(prtMrk, prtL, prtU)

    return bedMask, nozzleMask, partMask
# }}}

# getHsvValues {{{
def getHsvValues():
    bedLower = np.uint8([[150, 150, 150]])
    bedUpper = np.uint8([[255, 255, 255]])
    nozzleLower = np.uint8([[47, 35, 35]])
    nozzleUpper = np.uint8([[252, 255, 255]])
    partLower = np.uint8([[82, 50, 40]])
    partUpper = np.uint8([[110, 200, 200]])
    return bedLower, bedUpper, nozzleLower, nozzleUpper, partLower, partUpper
# }}}

# findCircles {{{
def findCircles(frameList, markerType, averageValue=10):
    averagedMarkers = None
    if len(frameList) > averageValue:
        averagedMarkers = getAverageCircles(frameList, markerType)
        del frameList[0]
    else:
        log.debug("Gathering {} frames".format(markerType))
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
        cv2.circle(image, (printHead[0], printHead[1]), 3, (255, 0, 0), 2)
    return image

#}}}

# filamentRunOut {{{
def filamentRunout(printHead, partBox):
    _, partY, _, _ = partBox
    _, pHeadY, _ = printHead
    if partY - pHeadY > 20:
        # TODO: Add a custom exception here for print run out

#}}}

# main {{{
def main():
    # setup {{{
    cap = cv2.VideoCapture("/dev/Cameras/MachineVision")
    bedFrames = []
    nozzleFrames = []
    partFrames = []
    averagedListValues = None
    avgBed = None
    avgNozzle = None
    printHead = None
    log.info("Setup complete")
    # }}}

    while True:

        try:
            # getImage {{{
            ret, image = cap.read()
            image = cv2.flip(image, 0)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            bedMask, nozzleMask, partMask = markerImage(image)
            bedImage = cv2.GaussianBlur(bedMask, (5, 5), 0)
            nozzleImage = cv2.GaussianBlur(nozzleMask, (5, 5), 0)
            partImage = cv2.GaussianBlur(partMask, (5, 5), 0)
            log.debug("Capture complete")
            # }}}

            # Bed Finding {{{
            bedFrames.append(bedImage)
            avgBed = findCircles(bedFrames, "bed")
            # }}}

            # Nozzle Finding{{{
            if avgBed:
                log.debug("Bed found")
                nozzleProcess = cropImage(nozzleImage, bedMarkers=avgBed)
                kernel = np.ones((1,1),np.uint8)
                nozzleProcess = cv2.morphologyEx(nozzleProcess, cv2.MORPH_OPEN, kernel)
                nozzleFrames.append(nozzleProcess)
                avgNozzle = findCircles(nozzleFrames, "nozzle")
                # }}}

            # Part Finding {{{
            if avgNozzle:  # If we find the bed and the nozzle find the part
                log.debug("Nozzle found")
                printHead = locPrintHead(avgNozzle)
                partProcess = cv2.medianBlur(partImage, 51)
                contours, hierarchy = cv2.findContours(partProcess, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                part = sorted(contours, key=cv2.contourArea, reverse=True)[0]
                bBox = cv2.boundingRect(part)
                cv2.rectangle(image, (bBox[0], bBox[1]), (bBox[0]+bBox[2], bBox[1]+bBox[3]), (0, 255, 0), 2)
            # }}}

            # Error Detection {{{


            # }}}


            drawCircles(image, avgBed, avgNozzle, printHead)
            cv2.imshow("3D Print", image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except cv2.error:
            pass
#}}}

if __name__ == '__main__':
    main()
