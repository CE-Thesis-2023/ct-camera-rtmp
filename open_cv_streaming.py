import os
import cv2
import pika
from dotenv import load_dotenv
from start_ffmpeg import start_ffmpeg 

from threading import Thread
from WebcamVideoStream import WebcamVideoStream
import pickle

load_dotenv()
rtmp_url = os.getenv('RTMP_URL')
server_ip = os.getenv("SERVER_IP")
rabbitmq_port = os.getenv("RABBITMQ_PORT")
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_pass = os.getenv("RABBITMQ_PASS")

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
    vs = WebcamVideoStream().start()
    vs.print()
    
    # RabbitMQ
    # Establish a connection to RabbitMQ
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    parameters = pika.ConnectionParameters(server_ip, rabbitmq_port , '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    frame_list = list()
    
    
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
            
            channel.basic_publish(exchange='', routing_key='frames', body=serialized_frames)
            # Empty the list
            frame_list = []

    # Close rabbitmq connection
    connection.close()
    
    ffmpeg_process.stdin.close()  # Close stdin pipe
    ffmpeg_process.wait()
    ffplay_process.kill()  # Forcefully close FFplay sub-process

if __name__ == '__main__':
        
    main()
