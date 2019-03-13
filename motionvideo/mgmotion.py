#MGMOTION - Calculate various motion features from a video file
# mgmotion computes a motion video, motiongram, quantity of motion, centroid of
# motion, width of motion, and height of motion from the video file or musical
# gestures data structure. The default method is to use plain frame differencing
# ('Diff'). A more expensive optical flow field can be calculated with the
# 'OpticalFlow' method. The mgmotion founction also provides a color mode, and the
# possibility to convert images with white on black instead of black on white. To
# use these modes, you need to set mode in the command, e.g.,
# mg.video.mode.color = 'On'
# mg.video.mode.convert = 'On'
#
# syntax:
# Call function with filename, method,starttime,endtime,filtertype,threshold
#
# input:
# filename: the name of the video file
# mg: instead of filename, uses a musical gestures data structure
# 'Diff', 'OpticalFlow': indicate the method used to compute the
# motion. 'Diff' method calculates the absolute frame difference between
# two successive frames. 'OpticalFlow' calculates the optical flow field
# filtertype: Binary, Regular, Blob. When choosing Blob, the element
# structure needs to be constructed using function strel
# thresh: threshold [0,1] (default=0.1)
#
# output:
# mg, a musical gestures data structure containing the computed motion
# image, motiongram, qom, com#
# mg = mginitstruct

import numpy as np
import os
import csv
import cv2
from scipy.signal import medfilt2d
from matplotlib import pyplot as plt
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

colorflag = 'true'


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message


def mg_videoreader(filename, method = 'Diff', filtertype = 'Regular', thresh = 0.1, starttime = 0, endtime = 0):

    #cut out relevant bit of video using starttime and endtime
    if starttime != 0 or endtime != 0:
        cropvideo = ffmpeg_extract_subclip(filename, starttime, endtime, targetname="cut.avi")
        video = cv2.VideoCapture("cut.avi")
    #or just use whole video
    else:
        video = cv2.VideoCapture(filename)

    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))

    #overwrite the inputvalue for endtime to not cut the video at 0...
    if endtime == 0:
        endtime = length/fps

    return video, length, fps, endtime


def mg_centroid(image, width, height, colorflag):
    #mgcentroid computes the centroid of an image/frame.

    if colorflag == 'true':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    x = np.linspace(1,width,width); y = np.linspace(1,height,height)
    qom = cv2.sumElems(image) #deles på width*height
    mx = np.mean(image,axis=0)
    my = np.mean(image,axis=1)
    comx = x*mx/sum(mx)
    comy = y*my/sum(my)
    com = [comx,comy]

    return com, qom

def mg_motion(filename, method = 'Diff', filtertype = 'Regular', thresh = 0.1, starttime = 0, endtime = 0):
    #spatial blur før terskling, dilate,. thresh = neg og over 1. velge hoppstørrelse: antall frames øvre grense.
    ii = 0
    filenametest = 'true'
    for c in filename:
        if c.isalpha() == True or c.isnumeric() == True or c == '.':
            pass
        else: 
            filenametest = 'false'

    if filenametest == 'true':
        if method != 'Diff' and method != 'OpticalFlow':
            msg = 'Please specify a method for motion estimation as str: Diff or OpticalFlow.'
            raise InputError(msg) 

        if filtertype != 'Regular' and filtertype != 'Binary':
            msg = 'Please specify a filter type as str: Regular or Binary'
            raise InputError(msg)

        if not isinstance(thresh,float) and not isinstance(thresh, int):
            msg = 'Please specify a threshold as a float.'
            raise InputError(msg)

        if not isinstance(starttime,float) and not isinstance(starttime,int):
            msg = 'Please specify a starttime as a float.'
            raise InputError(msg)

        if not isinstance(endtime,float) and not isinstance(endtime,int):
            msg = 'Please specify a endtime as a float.'
            raise InputError(msg)

    else:
        msg = 'Minimum input for this function: filename as a str.'
        raise InputError(msg)



    cap, length, fps, endtime = mg_videoreader(filename, method, filtertype, thresh, starttime, endtime)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame = np.zeros([height,width])
    of = os.path.splitext(filename)[0] 
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(of + '_motion.avi',fourcc, fps, (width,height))
    #f = cap


    gramx = np.array([1,1])
    gramy = np.array([1,1])
    qom = [] #quantity of motion
    com = [] #centroid of motion
    #aom = [] #area of motion
    #wom = [] #width of motion
    #hom = [] #height of motion


    ii = 0
    while(cap.isOpened()):

        prev_frame=frame
        ret, frame = cap.read()

        
        if ret==True:
            # colorflag right here does not work yet
            #utgangspunktet argb
            """ 
            if colorflag == 'true':
                frame = frame
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            """
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = frame.astype(np.int16)
            if method == 'Diff':
                motion_frame = ((np.abs(frame-prev_frame)>(thresh*255))*frame).astype(np.uint8)
                motion_frame = medfilt2d(motion_frame, kernel_size=5)
            elif method == 'OpticalFlow':
                #Optical Flow not implemented yet!!!
                motion_frame = ((np.abs(frame-prev_frame)>(thresh*255))*frame).astype(np.uint8) 

            gramx = np.append(gramx,np.mean(motion_frame,axis=0))
            gramy = np.append(gramy,np.mean(motion_frame,axis=1))   
            motion_frame = cv2.cvtColor(motion_frame, cv2.COLOR_GRAY2BGR)
            out.write(motion_frame)
            combite, qombite = mg_centroid(motion_frame,width,height,colorflag)
            com.append(combite)
            qom.append(qombite)

            #cv2.imshow('frame',motion_frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #   break
        else:
            break
        ii+=1
        print('Processing %s%%' %(int(ii/length*100)), end='\r')
        
    
    # Gotta write a write and plotting function!
    csvdata = [qom, com]
    newfile = of +'_data.csv'
    #csvwrite(newfile, csvdata) # Need to write header info as well
    
    #mgmotionplot(cap)

    # Write Quantity of Motion and Centroid of Motion to file
    with open(newfile, mode='w') as f_:
        f = csv.writer(f_, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        f.writerow(qom)
        f.writerow(com)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

mg_motion("dance.avi", endtime = 5)
    