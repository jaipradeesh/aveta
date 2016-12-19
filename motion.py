import atexit
from itertools import izip_longest

from Adafruit_MotorHAT import Adafruit_MotorHAT as MotorHAT

def sgn(a):
    return 1 if a >= 0 else -1


def range_incl(a, b, abs_step_size=1):
    step_size = abs_step_size if a <= b else -abs_step_size
    endval = b+1 if a <= b else b-1
    return xrange(a, endval, step_size)


def turn_off_motors():
    mh = MotorHAT(addr=0x60)
    for i in range(1, 5):
        mh.getMotor(i).run(MotorHAT.RELEASE)


atexit.register(turn_off_motors)


def clamp_speed(speed):
    if speed < -255:
        return -255
    if speed > 255:
        return 255
    return speed


def equalize_speeds(s1, s2):
    mean = (s1 + s2) / 2
    return mean, mean


class MotionController(object):

    LEFT_MOTOR = 4
    RIGHT_MOTOR= 3

    STEP_SIZE = 3

    def __init__(self, motor_hat=None, verbose=True):
        if motor_hat is None:
            motor_hat = MotorHAT(addr=0x60)
        self.left_motor = motor_hat.getMotor(self.LEFT_MOTOR)
        self.right_motor = motor_hat.getMotor(self.RIGHT_MOTOR)
        self.left_speed = 0
        self.right_speed = 0
        self.left_direction = None
        self.right_direction = None

        self.left_motor.run(MotorHAT.FORWARD)
        self.right_motor.run(MotorHAT.FORWARD)

        self.verbose = verbose

    def speed_ahead(self, steps=1):
        self._speed(steps)

    def speed_back(self, steps=1):
        self._speed(-steps)

    def in_motion(self):
        return self.left_speed != 0 or self.right_speed != 0

    def step_towards_zero(self):
        """Update the speeds one step towards 0."""
        left_step = 0 if self.left_speed == 0\
                    else -sgn(self.left_speed)
        right_step = 0 if self.right_speed == 0\
                     else -sgn(self.right_speed)
        new_left_speed = clamp_speed(left_step * self.STEP_SIZE +
                                     self.left_speed)
        new_right_speed = clamp_speed(right_step * self.STEP_SIZE +
                                      self.right_speed)
        self._update_speed(new_left_speed, new_right_speed)


    def _speed(self, steps):
        new_left_speed = clamp_speed(steps * self.STEP_SIZE +
                                     self.left_speed)
        new_right_speed = clamp_speed(steps * self.STEP_SIZE +
                                      self.right_speed)
        self._update_speed(new_left_speed, new_right_speed)

    def turn_left(self):
        new_left_speed = clamp_speed(self.left_speed - self.STEP_SIZE)
        new_right_speed = clamp_speed(self.right_speed + self.STEP_SIZE)

        self._update_speed(new_left_speed, new_right_speed)

    def turn_right(self):
        new_left_speed = clamp_speed(self.left_speed + self.STEP_SIZE)
        new_right_speed = clamp_speed(self.right_speed - self.STEP_SIZE)
        self._update_speed(new_left_speed, new_right_speed)

    def straighten_course(self):
        new_left_speed, new_right_speed = equalize_speeds(
            self.left_speed, self.right_speed
        )
        self._update_speed(new_left_speed, new_right_speed)

    def stop(self):
        speeds = izip_longest(range_incl(self.left_speed, 0, self.STEP_SIZE),
                              range_incl(self.right_speed, 0, self.STEP_SIZE),
                              fillvalue=0)
        for left_speed, right_speed in speeds:
            self._update_speed(left_speed, right_speed)

    def halt(self):
        self._update_speed(0, 0)

    def _update_speed(self, left_speed, right_speed):

        if self.verbose:
            print("updating ({}, {}). Current: ({}, {})".format(left_speed, right_speed, self.left_speed, self.right_speed))

        if left_speed is None:
            left_speed = self.left_speed

        if right_speed is None:
            right_speed = self.right_speed

        if left_speed < 0 and self.left_speed >= 0:
            self.left_motor.setSpeed(0)
            self.left_motor.run(MotorHAT.BACKWARD)

        if right_speed < 0 and self.right_speed >= 0:
            self.right_motor.setSpeed(0)
            self.right_motor.run(MotorHAT.BACKWARD)

        if left_speed > 0 and self.left_speed <= 0:
            self.left_motor.setSpeed(0)
            self.left_motor.run(MotorHAT.FORWARD)

        if right_speed > 0 and self.right_speed <= 0:
            self.right_motor.setSpeed(0)
            self.right_motor.run(MotorHAT.FORWARD)

        self.left_motor.setSpeed(abs(left_speed))
        self.right_motor.setSpeed(abs(right_speed))

        self.left_speed = left_speed
        self.right_speed = right_speed

