from tkinter import Tk, Frame

from algorithms.BSplineAlgorithm import BSplineAlgorithm
from algorithms.DWAAlgorithm import DWAAlgorithm
from algorithms.GreedyAlgorithm import GreedyAlgorithm
from Board import Board
from Game import Game


class RobotSimulator(Frame):

    def __init__(self, algorithm: int):
        super().__init__()

        self.master.title("Robot simulator 2.0")
        game = Game(4)

        if algorithm == 0:
            self.board = Board(game, BSplineAlgorithm(game))
        elif algorithm == 1:
            self.board = Board(game, DWAAlgorithm(game))
        elif algorithm == 2:
            self.board = Board(game, GreedyAlgorithm(game))

        self.pack()


def main():
    root = Tk()
    RobotSimulator(1)
    root.mainloop()


if __name__ == '__main__':
    main()
