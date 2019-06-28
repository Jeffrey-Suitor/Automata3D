from statistics import mean
import numpy as np
import cv2
import time


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

#Global vars
scans = 10
markers = 4


# getAverageCircles {{{
def getAverageCircles(camera):

    #Setup
    count = 0
    averageList=[[], [], [], []]
    returnList = []

    while count < scans:

        # get image
        ret, image = cap.read()
        image = cv2.flip(image, 0)
        output = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # detect circles in the image
        circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,90,
                                param1=400, param2=16, minRadius=6, maxRadius=10) #TODO Tune these values

        if circles is not None: #If there are circles
            circles = np.uint16(np.around(circles))
            circles = circles[0] #Remove the one dimensional list
            if len(circles) == markers: #If we find the right number of circles
                count += 1
                print(count)
                circles = sorted(circles, key=lambda x:x[:][0]) #Sort circles by x
                for i in range(len(circles)):
                    averageList[i].append(circles[i])
                    # draw the outer circle

    for i in range(len(averageList)):
        tempList = np.mean(averageList[i], axis=0) #Get the average of the list
        returnList.append(tempList.tolist())
    for i in range(len(returnList)):
        for j in range(len(returnList[i])):
            returnList[i][j] = int(returnList[i][j]) #Convert all values to ints
    return returnList

# }}}

# cropImage {{{
def cropImage(image, markers):

    xMin = min(map(lambda x: x[0], markers))
    xMax = max(map(lambda x: x[0], markers))

    yMin = min(map(lambda x: x[1], markers))
    yMax = max(map(lambda x: x[1], markers))
    return image[yMin:yMax, xMin:xMax]

# }}}

# difImage {{{
#def difImage()
#}}}
if __name__ == '__main__':
    cap = cv2.VideoCapture("/dev/Cameras/MachineVision")
    averagedListValues = getAverageCircles(cap)
    ret, image = cap.read()
    image = cv2.flip(image, 0)
    output = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for circle in averagedListValues:
        cv2.circle(output, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
        cv2.circle(output, (circle[0], circle[1]), 2, (0, 0, 255), 3)
    output = cropImage(output, averagedListValues)
    cv2.imshow("output", output)
    cv2.waitKey(0)
