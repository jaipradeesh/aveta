def clamp_speed(speed):
    if speed < -255:
        return -255
    if speed > 255:
        return 255
    return speed


def equalize_speeds(s1, s2):
    mean = (s1 + s2) / 2
    return mean, mean

