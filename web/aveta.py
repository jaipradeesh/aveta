import os
import json
from flask import (
    Flask, request, session, g, redirect, url_for, abort, render_template, Response, jsonify
)
from camera import VideoCamera
from flask_socketio import SocketIO, send, emit
from Adafruit_MotorHAT import Adafruit_MotorHAT as motors


import eventlet
eventlet.monkey_patch()


def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


# To release all motors cleanly when we exit.
atexit.register(turnOffMotors)


wheel_motors = {
    "left": 3,
    "right": 4,
}


speed_step = 3




def change_speed(left_speed, right_speed):
    return (clamp_speed(left_speed + speed_step),
            clamp_speed(right_speed + speed_step))


def forward():
    left_speed, right_speed =\
            change_speed(left_speed, right_speed)


def backward():
    pass


left_speed, right_speed = 0, 0


app = Flask(__name__)
app.config.from_object(__name__)


app.config.update(dict(
    SECRET_KEY="%%rR8=_36Ptxt6zQMR`j",
    USERNAME="admin",
    PASSWORD="default",
))


@app.route("/steer/<direction>")
def steer(direction):
    print("Direction {} pushed.".format(direction))
    return jsonify({"success": True})

@app.route("/")
def home():
    return render_template("index.html")


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\nContent-Type: image/jpeg\r\n\n' + frame + b'\r\n\n')


@app.route("/video_feed")
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype="multipart/x-mixed-replace;boundary=frame")


socketio = SocketIO(app)

@socketio.on("message")
def handle_message(message):
    print("Received message: " + message)


@socketio.on("json")
def handle_json(json_msg):
    print("Received JSON: " + json_msg)


@socketio.on("steer")
def handle_steer(direction):
    print("Received args: direction={}".format(direction))


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
