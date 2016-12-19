import os
import sys
import json
import atexit
import multiprocessing as mp

import cv2


from flask import (
    Flask, request, session, g, redirect, url_for, abort, render_template, Response, jsonify
)
from flask_socketio import SocketIO, send, emit

sys.path.append("..")

import streaming
import streaming_plugins
from motion import MotionController
from video import VideoWriter
import cam

import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY="%%rR8=_36Ptxt6zQMR`j",
    USERNAME="admin",
    PASSWORD="default",
))

motionctl = MotionController()

def start_preview_process():
    streamer = streaming.Streamer(plugins=streaming_plugins.plugins,
                                  output_root="/home/pi/aveta/stream")
    proc = mp.Process(target=streamer.run)
    def shutdown():
        pid = proc.pid()
        proc.terminate()
        try:
            os.kill(pid, 0)
            proc.kill()
            print("Force stopped stream.py")
        except OSError:
            print("streaming process terminated gracefully.")
    atexit.register(shutdown)
    print("Starting preview process.")
    proc.start()


@app.route("/steer/<direction>")
def steer(direction):
    print("Direction {} pushed.".format(direction))
    return jsonify({"success": True})


@app.route("/")
def home():
    return render_template("index.html")


def video_stream():
    while True:
        with open("../stream/simple.jpeg", "rb") as fp:
            data = fp.read()
        yield(b'--frame\r\nContent-Type: image/jpeg\r\n\n' + data + b'\r\n\n')


@app.route("/videofeed")
def video_feed():
    return Response(video_stream(),
                    mimetype="multipart/x-mixed-replace;boundary=frame")

socketio = SocketIO(app)

@socketio.on("message")
def handle_message(message):
    print("Received message: " + message)


@socketio.on("json")
def handle_json(json_msg):
    print("Received JSON: " + json_msg)


@socketio.on("steer")
def handle_steer(data):
    print("Received args: data={}".format(data))
    cmd = data["cmd"]
    if cmd == "left":
        motionctl.turn_left()
    elif cmd == "right":
        motionctl.turn_right()
    elif cmd == "up":
        motionctl.speed_ahead()
    elif cmd == "down":
        motionctl.speed_back()
    elif cmd == "stop":
        motionctl.stop()
        


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
