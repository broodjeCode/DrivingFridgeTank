import sys
import os
from multiprocessing import Process, Queue, Manager
from time import sleep as sleep
import time
import numpy as np
import cv2
import picamera
import picamera.array
import imutils
from collections import deque


class cameraThread(Process):
        def __init__(self):
                self.debug=False

	def cameraThread(self, args):
		try:
			with picamera.PiCamera() as camera:
				with picamera.array.PiRGBArray(camera) as stream:
					## Setup camera capture resolution
					camera.resolution = (args["cwidth"],args["cheight"])
	
					## setup vars from args
					cameraResolution=(args["cwidth"],args["cheight"])
					processingResolution=(args["pwidth"],args["pheight"])
					daemon=args["daemon"]
					debug=args["cdebug"]
					pts = deque(maxlen=args["buffer"])

					## create window colorbars
					cv2.namedWindow('Colorbars')
					hh='Hue High'
					hl='Hue Low'
					sh='Saturation High'
					sl='Saturation Low'
					vh='Value High'
					vl='Value Low'
					wnd = 'Colorbars'
					cv2.createTrackbar(hl, wnd,155,179,nothing)
					cv2.createTrackbar(hh, wnd,179,179,nothing)
					cv2.createTrackbar(sl, wnd,123,255,nothing)
					cv2.createTrackbar(sh, wnd,255,255,nothing)
					cv2.createTrackbar(vl, wnd,72,255,nothing)
					cv2.createTrackbar(vh, wnd,190,255,nothing)

					while True: ## LOOP
						## reset empty vars
						radius=0

						## Set values from colorbars
						hul=cv2.getTrackbarPos(hl, wnd)
						huh=cv2.getTrackbarPos(hh, wnd)
						sal=cv2.getTrackbarPos(sl, wnd)
						sah=cv2.getTrackbarPos(sh, wnd)
						val=cv2.getTrackbarPos(vl, wnd)
						vah=cv2.getTrackbarPos(vh, wnd)
						HSVLOW=np.array([hul,sal,val])
						HSVHIGH=np.array([huh,sah,vah])

						## capture from camera
						camera.capture(stream, 'bgr', use_video_port=True)

						# stream.array now contains the image data in BGR order
						frame = stream.array
						frame = imutils.resize(frame, width=args["pwidth"], height=args["pheight"])

						blurred = cv2.GaussianBlur(frame, (11, 11), 0)
						if debug:
							cv2.imshow('blur', blurred)
							if cv2.waitKey(1) & 0xFF == ord('q'):
								break

						hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

						if debug:
							cv2.imshow('hsv', hsv)
							if cv2.waitKey(1) & 0xFF == ord('q'):
								break

						mask = cv2.inRange(hsv, HSVLOW, HSVHIGH)
						mask = cv2.erode(mask, None, iterations=2)
						mask = cv2.dilate(mask, None, iterations=2)

						if debug:
							cv2.imshow('mask', mask)
							if cv2.waitKey(1) & 0xFF == ord('q'):
								break

						cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
						cv2.CHAIN_APPROX_SIMPLE)[-2]
						center = None

						## If cnts > 0 Target locked!
						if len(cnts) > 0:
							objectDetected=True
							# find the largest contour in the mask, then use
							# it to compute the minimum enclosing circle and
							# centroid
							c = max(cnts, key=cv2.contourArea)
							((x, y), radius) = cv2.minEnclosingCircle(c)
							M = cv2.moments(c)
							center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

							# only proceed if the radius meets a minimum size
							if radius > 2 and debug == True:
								# draw the circle and centroid on the frame,
								# then update the list of tracked points
								cv2.circle(frame, (int(x), int(y)), int(radius),
									(0, 255, 255), 2)
								cv2.circle(frame, center, 5, (0, 0, 255), -1)
						else:
							objectDetected=False
						pts.appendleft(center)

						## Print location to console relative to image resolution from topleft to bottom right
						objectLocation=center

						if debug:
							for i in xrange(1, len(pts)):
							# if either of the tracked points are None, ignore
							# them
								if pts[i - 1] is None or pts[i] is None:
									continue

								# otherwise, compute the thickness of the line and
								# draw the connecting lines
								thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
								cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)


						## Display output
						if daemon == False:
							cv2.imshow('frame', frame)
							if cv2.waitKey(1) & 0xFF == ord('q'):
								break

						## publish data to queue
#						ocvQueue.put([cameraResolution, processingResolution, objectLocation, objectDetected, radius])

						# reset the stream before the next capture
						stream.seek(0)
						stream.truncate()
					raise Exception('Quit')
		except :
			print "cameraThread() CTRL+C"
