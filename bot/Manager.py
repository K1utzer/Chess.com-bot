import time
import pyautogui

from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QApplication, QMainWindow

from .ImageDetection import ImageDetection
from .ChessBoard import ChessBoard

class Manager(QMainWindow):

    def __init__(self):
        super(Manager, self).__init__()

        self.path = "pictures/"

        self.label_won_hidden = True
        self.label_lost_hidden = True
        self.started = False

        uic.loadUi("gui/main.ui", self)

        self.label_won.setHidden(self.label_won_hidden)
        self.label_lost.setHidden(self.label_lost_hidden)

        self.show()
        self.b_start.setEnabled(False)
        self.b_start.clicked.connect(self.start_bot)
        self.b_quit.clicked.connect(self.quit_programm)
        self.b_detect.clicked.connect(self.detect_board)
        self.b_Settings.clicked.connect(self.show_settings)


    def start_bot(self):
        self.started = True
        self.b_Settings.setEnabled(False)
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")
        self.field_Cords, self.myturn = self.imageDet.calculate_field_cords(self.board_coordinates[0], self.field_height, self.field_width, self)
    
    def detect_board(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")

        self.imageDet = ImageDetection(self)
        
        try:
            boardFound, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width = self.imageDet.searchBoard(
                f"{self.path}screen.png", self)
        except TypeError as e:
            boardFound = False
            print("Board not found!"+str(e))

        if boardFound:
            self.b_start.setEnabled(True)
            self.progressBarUpdate(0)

    def show_settings(self):
        pass

    def quit_programm(self):
        exit()

    def show_image(self, img_path):
        try:
            pixmap = QtGui.QPixmap(img_path)
            pixmap = pixmap.scaled(521, 521)
            self.label_image.setPixmap(pixmap)
            self.label_image.show()
        except Exception:
            pass
    


    def checkbox_automove_isChecked(self):
        return self.box_automove.isChecked()

    def progressBarUpdate(self, value):
        self.progressBar.setValue(value)

    def show_won(self):
        self.label_won_hidden = not self.label_won_hidden
        self.label_won.setHidden(self.label_won_hidden)


    def show_lost(self):
        self.label_lost_hidden = not self.label_lost_hidden
        self.label_lost.setHidden(self.label_lost_hidden)






def main():
    app = QApplication([])
    window = Manager()
    app.exec_()


