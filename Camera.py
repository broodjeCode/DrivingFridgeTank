import sys
import os
from multiprocessing import Process, Queue, Manager
import time	
import numpy as np
import cv2
import picamera
import picamera.array
import imutils
from collections import deque


class cameraThread(Process):
        def __init__(self,args): ## setup Program variables from args (from parents argparser)
		self.loopCompletedTime=1
                self.debug=args["cdebug"]
		self.setdaemon=args["daemon"]
		self.pwidth=args["pwidth"]
		self.pheight=args["pheight"]
		self.cwidth=args["cwidth"]
		self.cheight=args["cheight"]
		self.cdebug=args["cdebug"]
		self.buffer=args["buffer"]

	def nothing(self,na):
		pass


	def run(self,CameraDataOut):
#		try:
			with picamera.PiCamera() as camera:
				with picamera.array.PiRGBArray(camera) as stream:
					## Setup camera capture resolution
					camera.resolution = (self.cwidth,self.cheight)
	
					## setup vars from args
					cameraResolution=(self.cwidth,self.cheight)
					processingResolution=(self.pwidth,self.pheight)
					daemon=self.setdaemon
					debug=self.cdebug
					pts = deque(maxlen=self.buffer)

					## create window colorbars
					cv2.namedWindow('Colorbars')
					hh='Hue High'
					hl='Hue Low'
					sh='Saturation High'
					sl='Saturation Low'
					vh='Value High'
					vl='Value Low'
					wnd = 'Colorbars'
					cv2.createTrackbar(hl, wnd,0,179,self.nothing)
					cv2.createTrackbar(hh, wnd,3,179,self.nothing)
					cv2.createTrackbar(sl, wnd,253,255,self.nothing)
					cv2.createTrackbar(sh, wnd,255,255,self.nothing)
					cv2.createTrackbar(vl, wnd,57,255,self.nothing)
					cv2.createTrackbar(vh, wnd,110,255,self.nothing)

					while True: ## LOOP
						self.loopStartTime=time.time()
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
						frame = imutils.resize(frame, width=self.pwidth, height=self.pheight)

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
							center=(0,0)
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
								thickness = int(np.sqrt(self.buffer / float(i + 1)) * 2.5)
								cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)


						## Display output
						if daemon == False:
							cv2.imshow('frame', frame)
							if cv2.waitKey(1) & 0xFF == ord('q'):
								break

						## publish data to arrayOut
						CameraDataOut[0]=cameraResolution[0]
						CameraDataOut[1]=cameraResolution[1]
						CameraDataOut[2]=processingResolution[0]
						CameraDataOut[3]=processingResolution[1]
						CameraDataOut[4]=objectDetected
						CameraDataOut[5]=radius
						CameraDataOut[6]=objectLocation[0]
						CameraDataOut[7]=objectLocation[1]

						# reset the stream before the next capture
						stream.seek(0)
						stream.truncate()

						self.loopCompletedTime=(time.time() - self.loopStartTime) ### Aaaaand we're done.
						CameraDataOut[8]=self.loopCompletedTime ## publish time to arrayOut
					raise Exception('Quit')
#		except :
#			print "cameraThread() CTRL+C"
