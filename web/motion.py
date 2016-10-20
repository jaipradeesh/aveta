import atexit

from Adafruit_MotorHAT import Adafruit_MotorHAT as MotorHAT


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

    LEFT_MOTOR = 3
    RIGHT_MOTOR= 4

    STEP_SIZE = 3

    def __init__(self, motor_hat=None):
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


    def speed_ahead(self, steps=1):
        self._speed(steps)

    def speed_back(self, steps=1):
        self._speed(-steps)

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

    def _update_speed(self, left_speed, right_speed):

        print("updating ({}, {}). Current: ({}, {})".format(left_speed, right_speed, self.left_speed, self.right_speed))


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

