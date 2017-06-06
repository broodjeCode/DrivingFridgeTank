## include required modules
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


## Welcome to the main class
class ImageProcessor(Process):
        def __init__(self,args):

## Setup program variables from args (from parents argparser)
		self.loopCompletedTime=1
        self.debug=args["cdebug"]
		self.setdaemon=args["daemon"]
		self.pwidth=args["pwidth"]
		self.pheight=args["pheight"]
		self.cwidth=args["cwidth"]
		self.cheight=args["cheight"]
		self.cdebug=args["cdebug"]
		self.buffer=args["buffer"]

## This function is used by cv2.createTrackbar. createTrackbar has a mandatory callback function but we're not using that in our program.
	def nothing(self,na):
		pass

## This is the main function called from Robot.py to start the ImageProcessorThread and let it do it's thing.
	def run(self,CameraDataOut):
		with picamera.PiCamera() as camera: # Use camera
			with picamera.array.PiRGBArray(camera) as stream: # Define stream as RGBArray

## Setup camera and other program settings
				# Setup camera capture resolution
				camera.resolution = (self.cwidth,self.cheight)

				# setup vars from args
				cameraResolution=(self.cwidth,self.cheight)
				processingResolution=(self.pwidth,self.pheight)
				daemon=self.setdaemon
				debug=self.cdebug
				pts = deque(maxlen=self.buffer)

				# create window colorbars, we use this to debug/adjust object HSV color matching
				cv2.namedWindow('Colorbars')
				hh='Hue High'
				hl='Hue Low'
				sh='Saturation High'
				sl='Saturation Low'
				vh='Value High'
				vl='Value Low'
				wnd = 'Colorbars'

				# init the colorbars with default values.
				cv2.createTrackbar(hl, wnd,0,179,self.nothing)
				cv2.createTrackbar(hh, wnd,3,179,self.nothing)
				cv2.createTrackbar(sl, wnd,253,255,self.nothing)
				cv2.createTrackbar(sh, wnd,255,255,self.nothing)
				cv2.createTrackbar(vl, wnd,57,255,self.nothing)
				cv2.createTrackbar(vh, wnd,110,255,self.nothing)

				# This is the actual loop
				while True: ## LOOP
					# Define the startime so we can calculate processed FPS
					self.loopStartTime=time.time()

					# Reset empty vars
					radius=0

					# Set values from colorbars that we created above
					hul=cv2.getTrackbarPos(hl, wnd)
					huh=cv2.getTrackbarPos(hh, wnd)
					sal=cv2.getTrackbarPos(sl, wnd)
					sah=cv2.getTrackbarPos(sh, wnd)
					val=cv2.getTrackbarPos(vl, wnd)
					vah=cv2.getTrackbarPos(vh, wnd)
					HSVLOW=np.array([hul,sal,val])
					HSVHIGH=np.array([huh,sah,vah])

					# Capture frame from camera stream
					camera.capture(stream, 'bgr', use_video_port=True)

					# stream.array now contains the image data in BGR order
					frame = stream.array

					# Resize the image to the desired processing resolution
					frame = imutils.resize(frame, width=self.pwidth, height=self.pheight)

					# Apply a blur to reduce the noise, this will improve object tracking and reduce false detections
					blurred = cv2.GaussianBlur(frame, (11, 11), 0)

					# If args["cdebug"] == true display blurred image
					if debug:
						cv2.imshow('blur', blurred)
						if cv2.waitKey(1) & 0xFF == ord('q'):
							break
						hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

					# If args["cdebug"] == true display blurred image in HSC colors
					if debug:
						cv2.imshow('hsv', hsv)
						if cv2.waitKey(1) & 0xFF == ord('q'):
							break

					# Some processing to make a black/white picture with the detection, mask
					mask = cv2.inRange(hsv, HSVLOW, HSVHIGH)
					mask = cv2.erode(mask, None, iterations=2)
					mask = cv2.dilate(mask, None, iterations=2)

					# If args["cdebug"] == true display the mask image
					if debug:
						cv2.imshow('mask', mask)
						if cv2.waitKey(1) & 0xFF == ord('q'):
							break

					# Count the detected countours within mask (image)
					cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
					cv2.CHAIN_APPROX_SIMPLE)[-2]
					center = None

					# If cnts > 0 Target locked!
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
					# Object is not insight.
						objectDetected=False
						center=(0,0)

					# Add points for red tracer (only used when debugging is enabled
					pts.appendleft(center)

					# Store location relative to image resolution from topleft to bottom right
					objectLocation=center

					# If args["cdebug"] == true Draw the red tracer for debugging.
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

					# if not in daemon mode display the actual image as captured by the camera.
					if daemon == False:
						cv2.imshow('frame', frame)
						if cv2.waitKey(1) & 0xFF == ord('q'):
							break

					# Write new data to CameraDataOut, this is handled in Robot.py
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

					# Aaand we're done, so calculate the time and also store this to CameraDataOut
					self.loopCompletedTime=(time.time() - self.loopStartTime)
					CameraDataOut[8]=self.loopCompletedTime

				# Try to break nicely
				raise Exception('Quit')
