import time
import pyautogui


from threading import Thread
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QApplication, QMainWindow

from .ImageDetection import ImageDetection
from .ChessBoard import ChessBoard
from .StockfishManager import StockfishManager
from .config import Config
from .MouseControl import MouseControl

class Manager(QMainWindow):

    def __init__(self):
        super(Manager, self).__init__()
        self.running = False
        self.games_played = 0
        self.path = "pictures/"
        self.config = Config()

        self.started = False

        uic.loadUi("gui/main.ui", self)

        self.label_won.setHidden(True)
        self.label_lost.setHidden(True)

        self.show()
        self.b_start.setEnabled(False)
        self.b_start.clicked.connect(self.start_bot)
        self.b_quit.clicked.connect(self.quit_programm)
        self.b_detect.clicked.connect(self.detect_board)
        self.b_Settings.clicked.connect(self.show_settings)



    def start_bot(self):
        self.thread = Thread(target = self.run_bot, args = [])
        self.thread.start()
        self.thread.join()
    def run_bot(self):

        if self.games_played > 1:
            self.set_won(False)
            self.set_lost(False)
        self.games_played += 1
        self.started = True
        self.b_Settings.setEnabled(False)
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")
        imageDet = ImageDetection(self)
        self.field_Cords, self.myturn = imageDet.calculate_field_cords(self.board_coordinates[0], self.field_height, self.field_width, self)
        chessBoard = ChessBoard()
        stockfish = StockfishManager(self.config.stockfish_path_name)
        game_running = True
        bot_move = None
        while game_running:
            if chessBoard.getBoard().is_checkmate():
                game_running = False
                self.set_won(True) if not self.myturn else self.show_lost(True)
                break
            if self.myturn:
                bot_move = self.bot_Turn(stockfish, chessBoard)
            else:
                self.opponent_Turn(bot_move, chessBoard)

            #screenshot = pyautogui.screenshot()
            #screenshot.save(f"{self.path}turn_screen.png")
            #imageDet.saveResizedImag(f"{self.path}turn_screen.png", 
            #       self.board_coordinates[0][1], self.board_coordinates[0][0], self.board_coordinates[0][1]*self.board_height, self.board_coordinates[0][0]*self.board_width)
            #self.show_image(f"{self.path}turn_screen.png")
        self.thread = None

    
    def bot_Turn(self, stockfish: StockfishManager, chessBoard):
        best_move = stockfish.get_best_move(chessBoard.getBoard())
        chessBoard.makeMove(best_move)
        mouseContr = MouseControl()
        mouseContr.mousePos(
            self.field_Cords[best_move[:2]][0], self.field_Cords[best_move[:2]][1])
        mouseContr.mouseClick()
        mouseContr.mousePos(
            self.field_Cords[best_move[2:4]][0], self.field_Cords[best_move[2:4]][1])
        mouseContr.mouseClick()
        self.myturn = False

    def opponent_Turn(self, bot_move, chessBoard):
        if bot_move is None:
            bot_move = ""
        fmove = False
        smove = False
        screenshot = pyautogui.screenshot()
        screenshot.save("pictures/turn_screen.png")
        imagDet = ImageDetection(self)
        screen = imagDet.loadImag("pictures/turn_screen.png")
        
        for field in self.field_Cords:
            x = self.field_Cords[field][0]
            y = self.field_Cords[field][1]
            x2 = int(x+(self.field_width/2)-10)
            y2 = int(y+(self.field_height/2)-10)
            
            if (screen[y2, x2][0] <= 115 and
                screen[y2, x2][1] >= 235 and
                    screen[y2, x2][2] >= 235):
                yellow_white = [screen[y2, x2][0],
                                screen[y2, x2][1], screen[y2, x2][2]]
                if list(screen[y+10, x]) == yellow_white:
                    fmove = field
                else:
                    smove = field
            
            if (screen[y2, x2][0] <= 55 and
                screen[y2, x2][0] >= 34 and
                screen[y2, x2][1] <= 215 and
                screen[y2, x2][1] >= 193 and
                screen[y2, x2][2] <= 198 and
                    screen[y2, x2][2] >= 177):
                yellow_green = [screen[y2, x2][0],
                                screen[y2, x2][1], screen[y2, x2][2]]
                if list(screen[y+10, x]) == yellow_green:
                    fmove = field
                else:
                    smove = field

        if fmove and smove and str(fmove+smove) not in bot_move:
            try:
                chessBoard.makeMove(f"{fmove}{smove}")
                self.myturn = True
                print()
                print(f"\nOpponent move: {fmove}{smove}")
                print(chessBoard.getBoard())
            except ValueError:
                time.sleep(1)
                return
    def detect_board(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")

        imageDet = ImageDetection(self)
        
        try:
            boardFound, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width = imageDet.searchBoard(
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

    def set_won(self, show):
        self.label_won.setHidden(not show)


    def set_lost(self, show):
        self.label_lost.setHidden(not show)






def main():
    app = QApplication([])
    window = Manager()
    app.exec_()

    


