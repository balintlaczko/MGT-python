import cv2
import numpy as np
import os
from ._utils import mg_progressbar, MgImage


def mg_average_image(self, filename='', normalize=True):
    """
    Finds and saves an average image of an input video file.

    Parameters
    ----------
    - filename : str, optional

        Path to the input video file. If not specified the video file pointed to by the MgObject is used.
    - normalize : bool, optional

        Default is `True`. If `True`, normalizes pixel values in the output image.

    Outputs
    -------
    - `filename`_average.png

    Returns
    -------
    - MgImage

        A new MgImage pointing to the output '_average' image file.
    """

    if filename == '':
        filename = self.filename

    of = os.path.splitext(filename)[0]
    video = cv2.VideoCapture(filename)
    ret, frame = video.read()
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    if self.color == False:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    average = frame.astype(np.float)/length
    ii = 0
    while(video.isOpened()):
        ret, frame = video.read()
        if ret == True:
            if self.color == False:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = np.array(frame)
            frame = frame.astype(np.float)
            average += frame/length
        else:
            mg_progressbar(
                length, length, 'Rendering average image:', 'Complete')
            break
        ii += 1
        mg_progressbar(ii, length, 'Rendering average image:', 'Complete')

    if self.color == False:
        average = cv2.cvtColor(average.astype(np.uint8), cv2.COLOR_GRAY2BGR)

    if normalize:
        average = average/np.max(average)*255
        average = average.astype(np.uint8)
        average_hsv = cv2.cvtColor(average, cv2.COLOR_BGR2HSV)
        average_hsv[:, :, 2] = cv2.equalizeHist(average_hsv[:, :, 2])
        average = cv2.cvtColor(average_hsv, cv2.COLOR_HSV2BGR)

    cv2.imwrite(of+'_average.png', average.astype(np.uint8))

    return MgImage(of+'_average.png')
