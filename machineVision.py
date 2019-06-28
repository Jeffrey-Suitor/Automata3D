# import the necessary packages
import numpy as np
import cv2
# load the image, clone it for output, and then convert it to grayscale
cap = cv2.VideoCapture("/dev/Cameras/MachineVision")
while True:
    ret, image = cap.read()
    #image = cv2.imread("/home/jeff/Code/python/Automata3D/index.jpg")
    output = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect circles in the image
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,100,
                               param1=50, param2=30, minRadius=0, maxRadius=20) #TODO Tune these values
    # ensure at least some circles were found
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(output,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(output,(i[0],i[1]),2,(0,0,255),3)

    # show the output image
    cv2.imshow("output", np.hstack([image, output]))
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
