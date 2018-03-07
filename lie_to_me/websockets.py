"""
    Dependent file of Flask Socketio
    Sets up the various socket call endpoints
"""
from flask_socketio import emit, disconnect
from flask import request
from lie_to_me import socketio
from lie_to_me.process import base64_frames

# keeps track of frame being sent (0 to len(base64_frames))
# stored as a list to allow for referencing
current_frame = [0]


# An active connection exists between client and server
@socketio.on('connect')
def handle_connect():
    print('Client connected')


# Client has been disconnected
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


# Server received a message from Client
@socketio.on('message')
def handle_message_receival(json):
    print('Received: {0}'.format(str(json)))


# Affectiva Client ready to receive photos (base64_images)
@socketio.on('ready_receive')
def handle_ready_receive(json):
    print('Client Ready to Recieve: {0}'.format(str(json)))
    global current_frame

    if current_frame[0] < len(base64_frames):
        emit('next_frame', [current_frame[0], base64_frames[current_frame[0]]])
        current_frame[0] += 1

# Affectiva Client is requesting the next frame and submitting the
# emotion data of the previous frame in format json
@socketio.on('next_frame')
def handle_next_frame_request(json):
    global current_frame

    print("Previous frame data: {0}".format(str(json)))

    # anger, contempt, disgust, engagement, fear, joy, sadness, surprise, valence
    emotions = json['data'][0]['emotions']
    expressions = json['data'][0]['expressions']

    eye_closure = expressions['eyeClosure']

    print(emotions)
    print(eye_closure)

    exit()

    if current_frame[0] < len(base64_frames):
        emit('next_frame', [current_frame[0], base64_frames[current_frame[0]]])
        current_frame[0] += 1
    else:
        emit('no_more_frames', 'Completed')
        disconnect()
