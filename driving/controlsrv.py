"""This is an HTTP server to directly set speeds on the robot."""
import sys

from flask import (
    Flask, request, session, g, redirect, url_for, abort, render_template,
    Response, jsonify
)

sys.path.append("..")
from motion import MotionController

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY="%%rR8=_36Ptxt6zQMR`j",
    USERNAME="admin",
    PASSWORD="default",
))

def make_err(errstring, code=500):
    response = jsonify({"success": False, "error": errstring})
    response.status_code = code
    return response


ctrl = MotionController()

@app.route("/set_speed/", methods=["POST"])
def set_speeds():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("Error parsing json payload: {}".format(e))
        raise e

    try:
        left_speed, right_speed = data["left"], data["right"]
    except KeyError:
        return make_err('input should be of the form {"left": <left-speed>, '
                        '"right": <right-speed>}', code=400)

    ctrl._update_speed(left_speed, right_speed)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

