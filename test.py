import cv
from opencv import highgui

cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
capture = cv.CaptureFromCAM(0)

def repeat():

    frame = cv.QueryFrame(capture)
    cv.ShowImage("w1", frame)
    c = highgui.cvWaitKey(5)


while True:
    repeat()
