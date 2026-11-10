from djitellopy import Tello
import time
import sys
import cv2 as cv 
import numpy as np


def main():
    choice = input('Testing with laptop or tello feed? (1 | 2): ')

    if choice == '1':
        cap = cv.VideoCapture(0)
        cap.set(3,400)
        cap.set(4,300)
        cap.set(10,100)

        while True:
            ret, frame = cap.read() 
            frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            #cv.imshow('Webcam', frame_hsv)
        
            mask = cv.inRange(frame_hsv, (61,102,104), (80,255,255))
            result = cv.bitwise_and(frame,frame,mask=mask)

            center = bounding_rectangle(mask, result)

            if center:
                x,y = center
                error = x - frame.shape[1]//2
                print(error)
                if x < frame.shape[1]//6:
                    d.send_rc_control(-25, 0, 0, 0)
                    cv.putText(result, '<--', (150,200), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
                elif x > (frame.shape[1]//6)*5:
                    d.send_rc_control(25, 0, 0, 0)
                    cv.putText(result, '-->', (150,200), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
                else:
                    cv.putText(result, 'middle', (150,200), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
            else:
                cv.putText(result, 'no item seen', (150,200), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
            
            cv.imshow('final result', result)
            cv.imshow('raw', frame)

            if cv.waitKey(20) & 0xFF == ord('q'):
                break


    elif choice == '2':
        d = Tello()

        try:
            d.connect()
        except Exception:
            d.land()
            d.end()
            sys.exit('Drone failed to connect.')

        print(f'Battery: {d.get_battery()}')
        print(f'Temperature: {d.get_temperature()}')

        if input('Press Q to land. Read according stats. Do you want to proceed with takeoff? (Y/N): ') == 'Y':
            try:
                d.takeoff()
                d.streamon()
                f = d.get_frame_read()

                time.sleep(2) #let the drone settle, or rc_send_control will fail

                while True:

                    frame = f.frame # NP array frame = the tello's frame attribute
                    frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
                    #cv.imshow('Webcam', frame_hsv)
                
                    mask = cv.inRange(frame_hsv, (61,102,104), (80,255,255))
                    result = cv.bitwise_and(frame,frame,mask=mask)
                
                    center = bounding_rectangle(mask, result)

                    
                    if center:
                        x,y = center
                        error = x - frame.shape[1]//2
                        if x < frame.shape[1]//6:
                            d.send_rc_control(-25, 0, 0, 0)
                            cv.putText(result, '<--', (150,200), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
                        elif x > (frame.shape[1]//6)*5:
                            d.send_rc_control(25, 0, 0, 0)
                            cv.putText(result, '-->', (150,200), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
                        else:
                            cv.putText(result, 'middle', (150,200), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
                            d.send_rc_control(0,0,0,0)
                    else:
                        #d.send_rc_control(0,0,0,0)
                        cv.putText(result, 'no item seen', (150,200), cv.FONT_HERSHEY_COMPLEX, 2, (255,255,255), 3)
                    
                    cv.imshow('tello feed', result)
                    cv.imshow('tello feed raw', frame)

                    if cv.waitKey(20) & 0xFF == ord('q'):
                        break

                    if d.get_battery() < 20:
                        print('Drone battery low. Preparing automatic landing...')
                        break


            finally:
                d.land()
                d.end()
                sys.exit('Thank you for flying Bird.E')
        else:
            print('Understood. Flight will not begin')
    else:
        print('Invalid choice. Run program again.')        
    

def bounding_rectangle(mask, final):
    contours,hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # tutorial suggested RETR_EXTERNAL and CHAIN_APPROX_NONE
    cv.drawContours(final, contours, -1, (255,0,0), 3)
    
    if contours:
        cnt = max(contours, key=cv.contourArea)
        x,y,w,h = cv.boundingRect(cnt)
        cv.rectangle(final, (x,y), ((x+w),(y+h)), (255,255,0), 3)
        return (x+(x+w))//2,(y+(y+h))//2


#def controller():




if __name__ == '__main__':
    main()