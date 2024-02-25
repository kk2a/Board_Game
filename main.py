from game.connect4 import app as coa, settings as cos
from game.dots_and_boxes import app as dba, settings as dbs
from game.gomokunarabe import app as gma, settings as gms
from game.othello import app as ota, settings as ots
from game.yacht import app as yaa, settings as yas

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QDialog, QLabel, QLineEdit

win_x = 300
win_y = 100
delta = 30
win_w = 300
win_h = 100

def connect4():
    settings = cos.GameSettings(win_x + delta, win_y + delta)
    if settings.exec():
        w, h = settings.get_settings()
        coa.Game(w, h)

def dots_boxes():
    settings = dbs.GameSettings(win_x + delta, win_y + delta)
    if settings.exec():
        disp_w, disp_h, dots_w, dots_h = settings.get_settings()
        dba.Game((disp_w, disp_h), (dots_w, dots_h))

def gomo():
    settings = gms.GameSettings(win_x + delta, win_y + delta)
    if settings.exec():
        w, h = settings.get_settings()
        gma.Game(w, h)

def othello():
    settings = ots.GameSettings(win_x + delta, win_y + delta)
    if settings.exec():
        w, h, n = settings.get_settings()
        ota.Game(w, h, n)

def yacht():
    settings = yas.GameSettings(win_x + delta, win_y + delta)
    if settings.exec():
        w, h = settings.get_settings()
        yaa.Game(w, h)

class GameSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Game Selector')
        self.setGeometry(win_x, win_y, win_w, win_h)
        layout = QVBoxLayout()

        game_category = ("Connect Four", "Dots and Boxes", "Gomokunarabe",
                         "Othello", "Yacht")
        co = (connect4, dots_boxes, gomo, othello, yacht)
        btn_games = [QPushButton(s, self) for s in game_category]
        for i in range(len(btn_games)):
            btn_games[i].clicked.connect(co[i])
            layout.addWidget(btn_games[i])

        self.setLayout(layout)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game_selector = GameSelector()
    sys.exit(app.exec())
