import os
import cv2
import pika
from dotenv import load_dotenv
import pickle
from start_ffmpeg import start_ffmpeg 

from threading import Thread
from WebcamVideoStream import WebcamVideoStream

load_dotenv()
rtmp_url = os.getenv('RTMP_URL')
rabbitmq_url = os.getenv('RABBITMQ_URL')

# This is the XML location + file containing the pre-trained classifier for detecting frontal faces in images
# face_cascade = cv2.CascadeClassifier('./pretrainned-model/haarcascade_frontalface_default.xml')
# def face_detection(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minSize=(30, 30))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#     return cv2.flip(frame, 1)

# create a thread pool with 2 threads

def main():
    vs = webcamVideoStream().start()
    vs.print()
    
    # RabbitMQ
    # Establish a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_url))
    channel = connection.channel()
    frame_list = []
    
    
    ffmpeg_process = start_ffmpeg(rtmp_url)

    # Read web camera
    while vs.isOpened():
        frame = vs.read()
      
        # Detect faces
        # frame = face_detection(frame)

        # Write to pipe
        ffmpeg_process.stdin.write(frame.tobytes())
        
        # Append the frame to the list
        frame_list.append(frame)
        if len(frame_list) == 10:
            serialized_frames = pickle.dumps(frame_list)
            # Send the list of frames to RabbitMQ
            
            Thread(channel.basic_publish, args=('', 'frames', serialized_frames)).start()
            # Empty the list
            frame_list = []

    # Close rabbitmq connection
    connection.close()
    
    ffmpeg_process.stdin.close()  # Close stdin pipe
    ffmpeg_process.wait()
    ffplay_process.kill()  # Forcefully close FFplay sub-process

if __name__ == '__main__':
        
    main()
