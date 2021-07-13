
#used to find euclidean distance betwwen two points
from scipy.spatial import distance as dist
from imutils.video import VideoStream
#identify the face
from imutils import face_utils
from threading import Thread
import numpy as np
#play sound
import playsound
#detect edges
import imutils
import time
import dlib
import cv2

def sound_alarm(path):
	# play an alarm sound
	print ("blinked")
	playsound.playsound(path)

def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)

	# return the eye aspect ratio
	return ear

#centre point of eye 
EYE_AR_THRESH = 0.2
 
EYE_AR_CONSEC_FRAMES = 20

COUNTER = 0
ALARM_ON = False


print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

def Detection():
        # start the video stream thread
        print("[INFO] starting video stream thread...")
        vs = VideoStream(src=0).start()
        time.sleep(1.0)

        # loop over frames from the video stream
        while True:
                
                frame = vs.read()
                frame = imutils.resize(frame, width=500)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # detect faces in the grayscale frame
                rects = detector(gray, 0)

                # loop over the face detections
                for rect in rects:
                        
                        shape = predictor(gray, rect)
                        shape = face_utils.shape_to_np(shape)

                        # extract the left and right eye coordinates, then use the
                        # coordinates to compute the eye aspect ratio for both eyes
                        leftEye = shape[lStart:lEnd]
                        rightEye = shape[rStart:rEnd]
                        leftEAR = eye_aspect_ratio(leftEye)
                        rightEAR = eye_aspect_ratio(rightEye)

                        
                        ear = (leftEAR + rightEAR) / 2.0

                        #extract left eye and right eye,draw points
                        leftEyeHull = cv2.convexHull(leftEye)
                        rightEyeHull = cv2.convexHull(rightEye)
                        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                        # check to see if the eye aspect ratio is below the blink
                        # threshold, and if so, increment the blink frame counter
                        if ear < EYE_AR_THRESH:
                                COUNTER += 1

                                
                                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                                        # if the alarm is not on, turn it on
                                        if not ALARM_ON:
                                                ALARM_ON = True

                                                
                                                t = Thread(target=sound_alarm,args=("alarm.wav",))
                                                t.deamon = True
                                                t.start()

                                        # draw an alarm on the frame
                                        cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                        # otherwise, the eye aspect ratio is not below the blink
                        # threshold, so reset the counter and alarm
                        else:
                                COUNTER = 0
                                ALARM_ON = False
                        #write text on the image
                        
                        cv2.putText(frame, "Eye Ratio: {:.2f}".format(ear), (300, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
         
                # show the frame
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                        break


        cv2.destroyAllWindows()
        vs.stop()
