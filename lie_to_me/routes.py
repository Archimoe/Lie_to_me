""" Routes of Flask Web Application """
import os
import csv
import threading
import shelve
from pathlib import Path
from flask import render_template, request, jsonify
from lie_to_me import app, video, basedir
from lie_to_me.process import process_video, process_audio


@app.route('/', methods=['GET', 'POST'])
def upload():
    """ Home Page Route
        Upload and Analyze Video
    :return: home.html template
    """
    if request.method == 'POST' and 'file' in request.files:
        # Video has been uploaded
        filename = video.save(request.files['file'])

        # Process video on a new thread
        threading.Thread(target=process_video, args=[os.path.join('uploads', filename)]).start()
        threading.Thread(target=process_audio, args=[os.path.join('uploads', filename)]).start()

        return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

    elif request.method == 'GET':
        return render_template('home.html')


@app.route('/analysis', methods=['GET'])
def analysis():
    """ Analysis Route
        View Final Analysis of Uploaded Video
    :return:
    """
    json_path = os.path.join(basedir, 'static', 'data', 'tmp_json')

    audio_file = Path(os.path.join(json_path, 'audio_data.shlf.db'))
    video_file = Path(os.path.join(json_path, 'facial_data.shlf.db'))
    csv_path = Path(os.path.join(basedir, 'static', 'data', 'csv'))

    # Files exists
    if audio_file.is_file() and video_file.is_file():
        with shelve.open(os.path.join(json_path, 'facial_data.shlf')) as shelf:
            emotion_data = shelf['emotion_data']
            microexpression_data = shelf['micro_expression_data']
            blink_data = shelf['blink_data']

        with shelve.open(os.path.join(json_path, 'audio_data.shlf')) as shelf:
            mean_energy = shelf['mean_energy']
            max_pitch_amp = shelf['max_pitch_amp']
            vowel_duration = shelf['vowel_duration']
            pitch_contour = shelf['pitch_contour']

    else:
        print(audio_file.is_file(), video_file.is_file())
        emotion_data = None
        print("no emotions")
        microexpression_data = None
        print("no microexpressions")
        blink_data = None
        print("no blinks")
        mean_energy = None
        print("no mean energy")
        max_pitch_amp = None
        print("no max pitch")
        vowel_duration = None
        print("no vowel duration")
        pitch_contour = None
        print("no pitch countour")

    # All output values should be available here:

    with open(Path(os.path.join(csv_path, 'train.csv')), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time Interval', 'Emotion Data', 'Micro-expressions', 'Blinks',
                         'Mean Energy', 'Max Pitch Amplitude', 'Vowel Duration', 'Fundamental Frequency'])
        for index in range(len(mean_energy)):
            writer.writerow([index, emotion_data[index], microexpression_data[index], blink_data[index],
                             mean_energy[index], max_pitch_amp[index], vowel_duration[index], pitch_contour[index]])

    return render_template('analysis.html', mean_energy=mean_energy, max_pitch_amp=max_pitch_amp,
                           vowel_duration=vowel_duration, pitch_contour=pitch_contour, blink_data=blink_data,
                           microexpression_data=microexpression_data, emotion_data=emotion_data)
