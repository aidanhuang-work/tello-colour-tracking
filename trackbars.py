import cv2 as cv 
import numpy as np
from djitellopy import Tello
import sys

CHOSEN_HUE = 24
CHOSEN_SAT = 101
CHOSEN_VAL =  107

mouse = None

class Trackbars:
    #def __init__(self):

    def __init__(self, min_hue, min_sat, min_val):
        cv.namedWindow('Trackbars')
        cv.createTrackbar('Min hue', 'Trackbars', min_hue, 179, nothing)
        cv.createTrackbar('Max hue', 'Trackbars', 179, 179, nothing)

        cv.createTrackbar('Min sat', 'Trackbars', min_sat, 255, nothing)
        cv.createTrackbar('Max sat', 'Trackbars', 255, 255, nothing)

        cv.createTrackbar('Min val', 'Trackbars', min_val, 255, nothing)
        cv.createTrackbar('Max val', 'Trackbars', 255, 255, nothing)

    def upper_trackbars(self):
        h_max = cv.getTrackbarPos('Max hue', 'Trackbars')
        s_max = cv.getTrackbarPos('Max sat', 'Trackbars')
        v_max = cv.getTrackbarPos('Max val', 'Trackbars')
        return np.array([h_max, s_max, v_max])

    def lower_trackbars(self):
        h_min = cv.getTrackbarPos('Min hue', 'Trackbars') 
        s_min = cv.getTrackbarPos('Min sat', 'Trackbars')
        v_min = cv.getTrackbarPos('Min val', 'Trackbars')
        return np.array([h_min, s_min, v_min])

def main():
    while True:
        choice = input('Testing with laptop feed or tello feed? (1 | 2): ')
        if choice == '1':
            laptop()
            break
        elif choice == '2':
            tello()
            break
        else:
            continue
        
def nothing(x):
    pass

def position(event, x, y, flags, param):
    global mouse
    mouse = x,y


tbars = Trackbars(CHOSEN_HUE, CHOSEN_SAT, CHOSEN_VAL) # Finds my green retainer case in normal bedroom lighting. It's hurt by shadows

def bounding_rectangle(mask, final):
    contours,hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # tutorial suggested RETR_EXTERNAL and CHAIN_APPROX_NONE
    cv.drawContours(final, contours, -1, (255,0,0), 3)
    
    if contours:
        cnt = max(contours, key=cv.contourArea)
        #perimeter = cv.arcLength(cnt,True)
        #approx = cv.approxPolyDP(cnt, perimeter*0.1, True)
        x,y,w,h = cv.boundingRect(cnt)
        cv.rectangle(final, (x,y), ((x+w),(y+h)), (255,255,0), 3)

        return (x+(x+w))//2,(y+(y+h))//2
        

def laptop():
    cap = cv.VideoCapture(0)
    cap.set(10, 100)

    final_window = 'green item'
    cv.namedWindow(final_window)
    cv.namedWindow('mask')

    cv.resizeWindow(final_window, (400,300)) # Tello size
    cv.resizeWindow('mask', (400,300))

    cv.setMouseCallback(final_window, position)
    while True:
        ret, frame = cap.read()
        frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        #cv.imshow('Webcam', frame_hsv)

        mask = cv.inRange(frame_hsv, tbars.lower_trackbars(), tbars.upper_trackbars())
        result = cv.bitwise_and(frame,frame,mask=mask)

        if mouse:
            cv.putText(result, f'{mouse[0]},{mouse[1]}', mouse, cv.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)

        center = bounding_rectangle(mask, result)
        if center:
            x,y = center
            if x < 554:
                cv.putText(result, '<--', (950,522), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
            elif x > 1290:
                cv.putText(result, '-->', (950,522), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
            else:
                cv.putText(result, 'middle', (950,522), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
        

        cv.imshow('mask', mask)
        cv.imshow(final_window, result)

        if cv.waitKey(10) & 0xFF == ord('q'):
            break

def tello():
    d = Tello()
    try:
        d.connect()
    except Exception():
        sys.exit('Could not connect to drone')
    d.streamon()
    f = d.get_frame_read()

    while True:
        frame = f.frame
        frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        #cv.imshow('Webcam', frame_hsv)

        mask = cv.inRange(frame_hsv, tbars.lower_trackbars(), tbars.upper_trackbars())
        result = cv.bitwise_and(frame,frame,mask=mask)


        center = bounding_rectangle(mask, result)
        if center:
            x,y = center
            if x < frame.shape[1]//3:
                cv.putText(result, 'on my left', (950,522), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
            elif x > (frame.shape[1]//3)*2:
                cv.putText(result, 'on my right', (950,522), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
            else:
                cv.putText(result, 'middle', (950,522), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
        else:
            cv.putText(result, 'nothing seen', (950,522), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
        

        cv.imshow('tello', result)

        if cv.waitKey(10) & 0xFF == ord('q'):
            d.end()
            break


if __name__ == '__main__':
    main()