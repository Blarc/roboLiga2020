# Regulator PID za obracanje na mestu.
# setpoint=0 pomeni, da naj bo kot med robotom in ciljem (target_angle) enak 0.
# Nasa regulirana velicina je torej kar napaka kota, ki mora biti 0.
# To velja tudi za regulacijo voznje naravnost.
from Classes.Constants import *


class PidController:
    def __init__(self):
        self.PID_turn: PID = PID(
            setpoint=0,
            kp=PID_TURN_KP,
            ki=PID_TURN_KI,
            kd=PID_TURN_KD,
            integral_limit=PID_TURN_INT_MAX)

        # PID za voznjo naravnost - regulira nazivno hitrost za oba motorja,
        # ki je odvisna od oddaljenosti od cilja.
        # setpoint=0 pomeni, da mora biti razdalja med robotom in ciljem enaka 0.
        self.PID_frwd_base: PID = PID(
            setpoint=0,
            kp=PID_STRAIGHT_KP,
            ki=PID_STRAIGHT_KI,
            kd=PID_STRAIGHT_KD,
            integral_limit=PID_STRAIGHT_INT_MAX)

        # PID za obracanje med voznjo naravnost.
        # setpoint=0 pomeni, da naj bo kot med robotom in ciljem (target_angle) enak 0.
        self.PID_frwd_turn: PID = PID(
            setpoint=0,
            kp=PID_TURN_KP,
            ki=PID_TURN_KI,
            kd=PID_TURN_KD,
            integral_limit=PID_TURN_INT_MAX)