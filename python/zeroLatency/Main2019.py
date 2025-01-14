#!/usr/bin/env python3

"""
Program za vodenje robota EV3
[Robo liga FRI 2019: Sadovnjak]
@Copyright: TrijeMaliKlinci
"""
import sys
from time import time
from ev3dev.ev3 import Button

from Connection import Connection
from Constants import SERVER_IP, GAME_ID, ROBOT_ID, TIMER_NEAR_TARGET
from Controller import Controller
from Entities import Team, GameData, HiveTypeEnum, State

# ------------------------------------------------------------------------------------------------------------------- #

print('Priprava tipal ... ', end='', flush=True)
btn = Button()
print('OK!')

url = SERVER_IP + GAME_ID
print('Vspostavljanje povezave z naslovom ' + url + ' ... ', end='', flush=True)
conn = Connection(url)
print('OK!')

print('Zakasnitev v komunikaciji s streznikom ... ', end='', flush=True)
print('%.4f s' % (conn.testDelay(numOfIterations=10)))

# ------------------------------------------------------------------------------------------------------------------- #

gameState = conn.request()

homeTeamTag = 'undefined'
enemyTeamTag = 'undefined'

team1 = Team(gameState["teams"]["team1"])
team2 = Team(gameState["teams"]["team2"])

if ROBOT_ID == team1.id:
    homeTeamTag = 'team1'
    enemyTeamTag = 'team2'
elif ROBOT_ID == team2.id:
    homeTeamTag = 'team2'
    enemyTeamTag = 'team1'
else:
    print('Robot ne tekmuje.')
    sys.exit(0)

print('Robot tekmuje in ima interno oznako "' + homeTeamTag + '"')

# ------------------------------------------------------------------------------------------------------------------- #
# GLOBAL VARIABLES

gameData = GameData(gameState, homeTeamTag, enemyTeamTag)
controller = Controller(initialState=State.GET_HEALTHY_HIVE)

robotNearTargetOld = False

target = None
timeOld = time()

# ------------------------------------------------------------------------------------------------------------------- #
# MAIN LOOP

print('Izvajam glavno zanko. Prekini jo s pritiskom na tipko DOL.')
print('Cakam na zacetek tekme ...')

doMainLoop = True
while doMainLoop and not btn.down:

    timeNow = time()
    loopTime = timeNow - timeOld
    timeOld = timeNow

    # Osveži stanje tekme.
    gameState = conn.request()
    if gameState == -1:
        print('Napaka v paketu, ponovni poskus ...')
    else:
        gameData = GameData(gameState, homeTeamTag, enemyTeamTag)
        controller.update(gameData, target)

        # Če tekma poteka in je oznaka robota vidna na kameri,
        # potem izračunamo novo hitrost na motorjih.
        # Sicer motorje ustavimo.

        # and robotAlive:
        if gameData.gameOn and controller.isRobotAlive():

            # ------------------------------------------------------------------------------------------------------- #
            # GET HEALTHY HIVE STATE

            if controller.state == State.GET_HEALTHY_HIVE:

                currentHive = controller.getClosestHive(HiveTypeEnum.HIVE_HEALTHY)

                if currentHive is None:
                    controller.state = State.GET_DISEASED_HIVE
                    continue

                controller.setTarget(currentHive.pos)

                if not controller.atTargetEPS():
                    controller.state = State.GET_TURN
                    robotNearTargetOld = False
                else:
                    controller.state = State.HOME

            # ------------------------------------------------------------------------------------------------------- #
            # GET DISEASED HIVE STATE

            elif controller.state == State.GET_DISEASED_HIVE:

                currentHive = controller.getClosestHive(HiveTypeEnum.HIVE_DISEASED)
                if currentHive is None:
                    # TODO tole ni uredu
                    controller.chassis.robotDie()
                else:
                    controller.setTarget(currentHive.pos)

                if not controller.atTargetEPS():
                    controller.state = State.GET_TURN
                    robotNearTargetOld = False
                else:
                    controller.state = State.ENEMY_HOME

            # ------------------------------------------------------------------------------------------------------- #
            # HOME STATE

            elif controller.state == State.HOME:

                target = gameData.homeBasket.topRight2
                target.x += 270
                target.y -= 515

                controller.setTarget(target)

                if not controller.atTargetEPS():
                    controller.state = State.HOME_TURN
                    robotNearTargetOld = False
                else:
                    controller.state = State.GET_HEALTHY_HIVE

            # ------------------------------------------------------------------------------------------------------- #
            # ENEMY HOME STATE

            elif controller.state == State.ENEMY_HOME:

                target = gameData.enemyBasket.topRight2
                target.x += 270
                target.y -= 515

                controller.setTarget(target)

                if not controller.atTargetEPS():
                    controller.state = State.ENEMY_HOME_TURN
                    robotNearTargetOld = False
                else:
                    controller.state = State.GET_HEALTHY_HIVE

            # ------------------------------------------------------------------------------------------------------- #
            # TURN STATE

            elif controller.state == State.GET_TURN:
                # Obračanje robota na mestu, da bo obrnjen proti cilju.

                if controller.stateChanged:
                    # Če smo ravno prišli v to stanje, najprej ponastavimo PID.
                    controller.resetPIDTurn()

                if controller.isTurned():
                    controller.state = State.GET_STRAIGHT

                else:
                    controller.updatePIDTurn()

            # ------------------------------------------------------------------------------------------------------- #
            # STRAIGHT STATE

            elif controller.state == State.GET_STRAIGHT:

                # Vmes bi radi tudi zavijali, zato uporabimo dva regulatorja.
                if controller.stateChanged:
                    controller.resetPIDStraight()
                    timeNearTarget = TIMER_NEAR_TARGET

                # Ali smo blizu cilja?
                if not robotNearTargetOld and controller.atTargetNEAR():
                    # Vstopili smo v bližino cilja.
                    # Začnimo odštevati varnostno budilko.
                    timeNearTarget = TIMER_NEAR_TARGET

                if controller.atTargetNEAR():
                    timeNearTarget = timeNearTarget - loopTime
                robotNearTargetOld = controller.atTargetNEAR()

                # Ali smo že na cilju?
                if controller.atTargetHIST():
                    controller.setSpeedToZero()
                    state = State.HOME

                elif timeNearTarget < 0:
                    # Smo morda blizu cilja, in je varnostna budilka potekla?
                    controller.setSpeedToZero()
                    state = State.GET_TURN

                else:
                    #  TODO multiplier v bližini cilja zmanjša PID, ker se tudi hitrost zmanjša
                    controller.updatePIDStraight()

            # ------------------------------------------------------------------------------------------------------- #
            # SPIN MOTORS

            controller.runMotors()

        else:
            # ------------------------------------------------------------------------------------------------------- #
            # BREAK MOTORS

            # Robot bodisi ni viden na kameri bodisi tekma ne teče.
            controller.breakMotors()

# Konec programa
controller.robotDie()
