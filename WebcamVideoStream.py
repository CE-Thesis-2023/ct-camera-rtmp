from threading import Thread
import cv2
from threading import Thread
class WebcamVideoStream:
    def __init__(self):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH ,1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT ,720)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        (self.grabbed, self.frame) = self.cap.read()
        self.stopped = False
        
    def start(self):
        # start the thread to read frames from the video stream
        Thread(self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            _, self.frame = self.cap.read()
   
    def read(self):
        # return the frame most recently read
        return self.frame
    
    def print(self):
        # Get video information
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(width, height, fps)

    def isOpened(self):
        return self.cap.isOpened()

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
