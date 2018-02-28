import os
import threading
from flask import render_template, request, jsonify, abort
from lie_to_me import app, video, basedir, socketio
from lie_to_me.process import process_video


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        filename = video.save(request.files['file'])

        threading.Thread(target=process_video, args=[os.path.join('uploads', filename)]).start()

        return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

    elif request.method == 'GET':
        print(basedir)
        return render_template('home.html')