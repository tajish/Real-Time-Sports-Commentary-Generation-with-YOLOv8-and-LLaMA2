from flask import Flask,render_template,request
from yolo import detectfootballs
import numpy as np
import subprocess


def convert_to_browser_mp4(input_path, output_path):
            command = [
                "ffmpeg",
                "-i", input_path,
                "-c:v", "libx264",   
                "-c:a", "aac",       
                "-strict", "-2",    
                output_path
            ]
            subprocess.run(command, check=True)
            return output_path

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


Allowed_Extention = ['mp4']

def allowed_extention(filename):
    return Allowed_Extention[0] == filename.split('.')[1]

@app.route('/upload',methods=['POST'])
def upload():
    if 'video' not in request.files:
        return 'No file Uploaded'
    video = request.files['video']
    if video.filename == '':
        return 'no file selected'
    if video and allowed_extention(video.filename):
        video.save('static/videos/'+video.filename)
        detectfootballs('static/videos/'+video.filename)
        convert_to_browser_mp4("static/videos/newd.mp4", "static/videos/output_new.mp4")
        video_filename = 'output_new.mp4'
        return render_template('preview.html', video_name=video_filename)
    return 'Wrong File Uploaded'
    


if __name__ == '__main__':
    app.run(debug=True)