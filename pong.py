import cv
import math
from opencv import highgui
import cmath

cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
capture = cv.CaptureFromCAM(0)

x = 320
y = 100                                                                                                      
v = 20
alpha = 0.25 * math.pi
r = 25

# from top-left to bottom right, horizontally
angles_ = ( 0.75, 0.5, 0.25, 
            1.00, -1,  0, 
            1.25, 1.5, 1.75)
angles = [math.pi * angle for angle in angles_]

def NormalizeAngle(angle):
    while angle > 2 * math.pi:
        angle -= 2 * math.pi

    while angle < 0:
        angle += 2 * math.pi

    return angle

angles = [NormalizeAngle(math.pi + angle) for angle in angles]

def Degrees(angle):
    if angle is None:
        return '(No angle)'
    return int(NormalizeAngle(angle) * 57.29)


def DiffLessThanPi(a, b):
    # normalize to 90 deg
    diff = a - (math.pi / 2)
    bprim = b - diff
    return NormalizeAngle(bprim) < math.pi

def GetCollision(x, y, r, data, size):
    points = ((x-r,y-r), (x, y-r), (x+r, y-r),
              (x-r, y),  (x, y),   (x+r, y),
              (x-r, y+r),(x, y+r), (x+r, y+r))
    
    npoints = 0
    sumangles = 0                                                                                                         

    for point, angle in zip(points, angles):
        if angle < 1:
            continue
        px = int(point[0])
        py = int(point[1])
        if px < 0 or px >= size[0] or py < 0 or py >= size[1]:
            continue
        if ord(data[px + size[0]*py]) > 0:
            npoints += 1
            sumangles += angle

    ang = None
    if npoints > 0:
        ang = sumangles / npoints
    print r, npoints, Degrees(ang)
    return (sumangles, npoints)

def DrawVector(img, center, alpha, length=15, thickness=2):
    dx = int(length * math.cos(alpha))
    dy = int(-length * math.sin(alpha))

    cv.Line(img, center, (center[0]+dx, center[1]+dy), 0, 2)

def repeat():
    global x, y, v, alpha, r
    frame = cv.QueryFrame(capture)
    cv.Flip(frame, None, 1)
    bw = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(frame, bw, cv.CV_BGR2GRAY)
    thresholded = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)

    size = cv.GetSize(frame)
    ball = cmath.rect(v, alpha)
    x += ball.real
    y -= ball.imag

    # Graaaavityyy no escape from graaavityyy
#    ball -= 0.9j
#    v, alpha = cmath.polar(ball)

    if x < r:
        x = r
        alpha = math.pi - alpha
    elif x > size[0] - r:
        x = size[0] - r - 2
        alpha = math.pi - alpha

    if y < r:
        y = r                                                       
        alpha = (2 * math.pi) - alpha
    elif y > size[1] - r:
        y = size[1] - r - 2
#        v -= 5
        alpha = (2 * math.pi) - alpha

    cv.Threshold(bw, thresholded, 50, 128, cv.CV_THRESH_BINARY_INV)
#    cv.Threshold(bw, thresholded, 128, 128, cv.CV_THRESH_BINARY)

    thresholded_median = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
    cv.Smooth(thresholded, thresholded_median, cv.CV_MEDIAN, 9)

    thresholded = thresholded_median

    data = thresholded.tostring()

    (sumangles, npoints) = GetCollision(x, y, r, data, size)

    angle = 666

    # jest kolizja, jest zabawa
    if npoints > 0 and npoints < 7:
        # angle - kat normalnej do powierzchni kolizji
        angle = sumangles / npoints
        newalpha = ((2 * angle) - alpha) 
#        ball = cmath.rect(v, newalpha)
#        normal = cmath.rect(npoints, angle)
#        ball += normal
#        newv, newalpha = cmath.polar(ball)
#        newalpha = 6 * alpha - 5 * angle
        newv = v
#        newv += npoints
        if not DiffLessThanPi(angle, newalpha):
            newalpha = newalpha - math.pi
        alpha = newalpha
        v = newv
#        nv = 1.5 * npoints
#        v = 0.5 * v + 0.5 * nv
        x += v * math.cos(alpha)
        y -= v * math.sin(alpha)
    elif npoints >= 7:
        print "ESCALATION"
        (sumangles, npoints) = GetCollision(x, y, 4*r, data, size)
        if npoints > 0 and npoints < 7:
            alpha = (sumangles / npoints)
            v = 15
        elif npoints >= 7:
            (sumangles, newpoints) = GetCollision(x, y, 8*r, data, size)
            if npoints > 0:
                alpha = (sumangles / npoints)
                v = 15
        
    alpha = NormalizeAngle(alpha)

    out = thresholded
    out = frame
    cv.Circle(out, (int(x), int(y)), r, 255, -1)
    DrawVector(out, (int(x), int(y)), alpha)
    if angle <> 666:
        DrawVector(out, (int(x), int(y)), angle, 20, 1)

    cv.AddWeighted(out, 0.9, thresholded, 0.2, out, 0.0)

#    cv.ShowImage("w1", frame)
        
    cv.ShowImage("w1", out)
    print alpha
    c = highgui.cvWaitKey(5)


while True:
    repeat()
