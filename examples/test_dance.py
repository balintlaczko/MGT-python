import sys
import os
sys.path.append('../mgmodule')
sys.path.append('..')
import mgmodule
import cv2

#import any non-module functions you want to use (see documentation) this way:
from _average import average_image

#CREATE MODULE OBJECT: Here is an example call to create an mg Object, using loads of parameters
mg = mgmodule.MgObject('dance.avi', starttime = 2, endtime = 7, color = False, contrast = 60)
#USE MODULE METHOD: To run the motionvideo analysis, run the function using your object
mg.mg_motionhistory()
#USE NON-MODULE FUNCTION, this one can find an average image of any video, here using the mb objects filename
average_image(mg.filename)
average_image('dance_trim_cb_motion.avi')
