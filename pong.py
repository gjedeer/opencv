import cv
import math
from opencv import highgui
import cmath
import random

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
              (x-r, y),  (-1, -1),   (x+r, y),
              (x-r, y+r),(x, y+r), (x+r, y+r))
    
    npoints = 0
    sumangles = 0                                                                                                         
    allpoints = 0

    for point, angle in zip(points, angles):
        px = int(point[0])
        py = int(point[1])
        if px < 0 or px >= size[0] or py < 0 or py >= size[1]:
            continue
        allpoints += 1
        if ord(data[px + size[0]*py]) > 0:
            npoints += 1
            sumangles += angle

    ang = None
    if npoints > 0:
        ang = sumangles / npoints
    print r, npoints, Degrees(ang)
    return (sumangles, npoints, allpoints)

def BallTrapped(bw):
    print "RUN PEDOBAER! ITS A TRAP!"
    global x, y
    size = cv.GetSize(bw)
    x = random.randint(0, size[0] - 1)
    y = random.randint(0, size[1] - 1)

def DrawVector(img, center, alpha, length=15, thickness=2):
    dx = int(length * math.cos(alpha))
    dy = int(-length * math.sin(alpha))

    cv.Line(img, center, (center[0]+dx, center[1]+dy), 0, 2)


# image buffers - to avoid reallocation
frame = cv.QueryFrame(capture)
bw = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
thresholded = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
median = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
median_color = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)

def repeat():
    global x, y, v, alpha, r
    frame = cv.QueryFrame(capture)

    # Odwroc w poziomie zeby ludziom wydawalo sie ze sa w lustrze
    cv.Flip(frame, None, 1)

    # informacje o kolorach raczej sie nie przydadza
    cv.CvtColor(frame, bw, cv.CV_BGR2GRAY)

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

    cv.Smooth(thresholded, median, cv.CV_MEDIAN, 9)

    data = median.tostring()

    (sumangles, npoints, allpoints) = GetCollision(x, y, r, data, size)

    angle = 666

    # jest kolizja, jest zabawa
    if npoints > 0 and npoints < allpoints:
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
    elif npoints >= allpoints - 1:
        print "ESCALATION"
        (sumangles, npoints, allpoints) = GetCollision(x, y, 4*r, data, size)
        if npoints > 0 and npoints < allpoints - 1:
            alpha = (sumangles / npoints)
            v = 15
        elif npoints >= allpoints - 1:
            (sumangles, newpoints, allpoints) = GetCollision(x, y, 8*r, data, size)
            if npoints > 0 and npoints < allpoints / 2:
                alpha = (sumangles / npoints)
                v = 15
            else:
                BallTrapped(median)
        
    alpha = NormalizeAngle(alpha)

    out = median
    out = frame
    cv.Circle(out, (int(x), int(y)), r, 255, -1)
    DrawVector(out, (int(x), int(y)), alpha)
    if angle <> 666:
        DrawVector(out, (int(x), int(y)), angle, 20, 1)

    # Wyswietlamy overlay z mapa kolizji
    cv.CvtColor(median, median_color, cv.CV_GRAY2BGR)
    cv.AddWeighted(out, 0.9, median_color, 0.2, 0.0, out)

#    cv.ShowImage("w1", frame)
        
    cv.ShowImage("w1", out)
    c = highgui.cvWaitKey(5)


while True:
    repeat()
