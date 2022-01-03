import time
from threading import Thread

import pyautogui
from PyQt5 import QtGui, uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from .ChessBoard import ChessBoard
from .config import Config
from .ImageDetection import ImageDetection
from .MouseControl import MouseControl
from .StockfishManager import StockfishManager



class Manager(QObject):
    finished = pyqtSignal()
    stopped_bot = pyqtSignal()
    progress = pyqtSignal(int)
    show_image = pyqtSignal(str)
    write_label = pyqtSignal(str)

    auto_move_update = pyqtSignal()

    set_board_coordinates = pyqtSignal(list)
    set_field_height = pyqtSignal(int)
    set_field_width = pyqtSignal(int)
    set_board_height = pyqtSignal(int)
    set_board_width = pyqtSignal(int)

    board_found = pyqtSignal(bool)

    path = "pictures/"
    game_running = True
    config = Config()
    counter = 0
    moves_counter = 0
    auto_move = False
    first_move = True
    game_stopped = False
    
    def __init__(self, parant, auto_move = None, board_coordinates = None, field_height = None, field_width = None, board_height = None, board_width = None):
        super(Manager, self).__init__()
        parant.stopped.connect(self.stopped)
        parant.automatic_move_change.connect(self.checkbox_change)
        
        self.board_coordinates = board_coordinates
        self.field_height = field_height
        self.field_width = field_width
        self.board_height = board_height
        self.board_width = board_width
        self.auto_move = auto_move

    def run(self):
        
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")
        imageDet = ImageDetection(self)
        
        self.field_Cords, self.myturn = imageDet.calculate_field_cords(
            self.board_coordinates[0], self.field_height, self.field_width, self)
        chessBoard = ChessBoard()

        try:
            stockfish = StockfishManager(self.config.stockfish_path_name)
        except Exception:
            self.write_label.emit("Stockfish path \nwrong")
            #self.stopped_bot.emit()
            self.game_stopped = True
        bot_move = None
        #counter = 0
        while self.game_running and not self.game_stopped:
            #counter += 1
            tmp_turn = self.myturn
            #self.progress.emit(counter)
            if chessBoard.getBoard().is_checkmate():
                self.game_running = False
                self.finished.emit()
                break
            if self.myturn:
                self.progress.emit(self.counter)
                #print("myturn")
                bot_move = self.bot_Turn(stockfish, chessBoard)
            else:
                #print("opponent turn")
                self.opponent_Turn(bot_move, chessBoard)
            time.sleep(1)
            if not tmp_turn == self.myturn and self.game_running:
                screenshot = pyautogui.screenshot()
                screenshot.save(f"{self.path}turn_screen.png")
                imageDet.saveResizedImag(f"{self.path}turn_screen.png",
                    self.board_coordinates[0][0], self.board_coordinates[0][1], self.board_coordinates[0][0]+self.board_width, self.board_coordinates[0][1]+self.board_height)
                self.update_image(f"{self.path}turn_screen.png")
                self.moves_counter += 1
            self.auto_move_update.emit()
        
        

    def bot_Turn(self, stockfish: StockfishManager, chessBoard):
        best_move = stockfish.get_best_move(chessBoard.getBoard())
        if self.auto_move:
            chessBoard.makeMove(best_move)
            self.write_label.emit(f"Bot move: {best_move}")
            mouseContr = MouseControl()
            mouseContr.mousePos(
                self.field_Cords[best_move[:2]][0], self.field_Cords[best_move[:2]][1])
            mouseContr.mouseClick()
            mouseContr.mousePos(
                self.field_Cords[best_move[2:4]][0], self.field_Cords[best_move[2:4]][1])
            mouseContr.mouseClick()
            self.myturn = False
        else:
            
            if self.first_move:
                self.write_label.emit(f"Best move: {best_move}")
                imageDet = ImageDetection(self)
                screenshot = pyautogui.screenshot()
                screenshot.save(f"{self.path}turn_screen.png")
                imageDet.draw_rec_on_img(
                    "pictures/turn_screen.png",
                    self.field_Cords[best_move[:2]][0]-int(self.field_width/2), 
                    self.field_Cords[best_move[:2]][1]-int(self.field_height/2), 
                    self.field_Cords[best_move[:2]][0]+int(self.field_width/2), 
                    self.field_Cords[best_move[:2]][1]+int(self.field_height/2))
                imageDet.draw_rec_on_img(
                    "pictures/turn_screen.png",
                    self.field_Cords[best_move[2:4]][0]-int(self.field_width/2), 
                    self.field_Cords[best_move[2:4]][1]-int(self.field_height/2),
                    self.field_Cords[best_move[2:4]][0]+int(self.field_width/2), 
                    self.field_Cords[best_move[2:4]][1]+int(self.field_height/2))
                imageDet.saveResizedImag(f"{self.path}turn_screen.png",
                    self.board_coordinates[0][0], self.board_coordinates[0][1], self.board_coordinates[0][0]+self.board_width, self.board_coordinates[0][1]+self.board_height)
                self.update_image("pictures/turn_screen.png")
                self.first_move = False

        screenshot = pyautogui.screenshot()
        screenshot.save("pictures/turn_screen.png")
        imagDet = ImageDetection(self)
        screen = imagDet.loadImag("pictures/turn_screen.png")
        fmove = False
        smove = False
        self.counter += 2
        if self.counter > 98:
            self.counter = 2
        for field in self.field_Cords:

            x = self.field_Cords[field][0]
            y = self.field_Cords[field][1]
            x2 = int(x+(self.field_width/2)-5)
            y2 = int(y-(self.field_height/2)+10)

            if (screen[y2, x2][0] <= 115 and
                screen[y2, x2][1] >= 235 and
                    screen[y2, x2][2] >= 235):
                yellow_white = [screen[y2, x2][0],
                                screen[y2, x2][1], screen[y2, x2][2]]
                if list(screen[y+int(self.field_height/2-13), x]) == yellow_white:
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
                if list(screen[y+int(self.field_height/2-13), x]) == yellow_green:
                    fmove = field
                else:
                    smove = field
            if fmove and smove:
                try:

                    chessBoard.makeMove(f"{fmove}{smove}")
                    self.myturn = False
                    print()
                    print(f"\Player move: {fmove}{smove}")
                    self.write_label.emit(f"Player move: \n{fmove}{smove}")
                    print(chessBoard.getBoard())
                    self.progress.emit(100)
                    self.counter = 0
                    self.first_move = True
                except ValueError:
                    return

    def opponent_Turn(self, bot_move, chessBoard):
        if self.counter == 0:
            self.write_label.emit(f"Waiting for\nOpponent move")
        self.counter += 2
        if self.counter > 98:
            self.counter = 2
        self.progress.emit(self.counter)
        if bot_move is None:
            bot_move = "xxx"
        
        screenshot = pyautogui.screenshot()
        screenshot.save("pictures/turn_screen.png")
        imagDet = ImageDetection(self)
        screen = imagDet.loadImag("pictures/turn_screen.png")
        fmove = False
        smove = False
        for field in self.field_Cords:
            
            x = self.field_Cords[field][0]
            y = self.field_Cords[field][1]
            x2 = int(x+(self.field_width/2)-5)
            y2 = int(y-(self.field_height/2)+10)

            if (screen[y2, x2][0] <= 115 and
                screen[y2, x2][1] >= 235 and
                    screen[y2, x2][2] >= 235):
                yellow_white = [screen[y2, x2][0],
                                screen[y2, x2][1], screen[y2, x2][2]]
                if list(screen[y+int(self.field_height/2-13), x]) == yellow_white:
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
                if list(screen[y+int(self.field_height/2-13), x]) == yellow_green:
                    fmove = field
                else:
                    smove = field
            if fmove and smove and str(fmove+smove) not in bot_move:
                try:
                    
                    chessBoard.makeMove(f"{fmove}{smove}")
                    self.myturn = True
                    print()
                    print(f"\nOpponent move: {fmove}{smove}")
                    self.write_label.emit(f"Opponent move: \n{fmove}{smove}")
                    print(chessBoard.getBoard())
                    self.progress.emit(100)
                    self.counter = 0
                except ValueError:
                    return
            #if not fmove and not smove and self.moves_counter > 0:
            #    screenshot = pyautogui.screenshot()
            #    screenshot.save(f"{self.path}turn_screen.png")
            #    imagDet.saveResizedImag(f"{self.path}turn_screen.png",
            #                             self.board_coordinates[0][0], self.board_coordinates[0][1], self.board_coordinates[0][0]+self.board_width, self.board_coordinates[0][1]+self.board_height)
            #    self.update_image(f"{self.path}turn_screen.png")
            #    print("Finished")
            #    self.game_running = False
            #    break
            #time.sleep(1)



    def detect_board(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")

        imageDet = ImageDetection(self)

        try:
            boardFound, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width = imageDet.searchBoard(
                f"{self.path}screen.png")
            self.set_board_coordinates.emit(self.board_coordinates)
            self.set_field_height.emit(self.field_height)
            self.set_field_width.emit(self.field_width)
            self.set_board_height.emit(self.board_height)
            self.set_board_width.emit(self.board_width)
        except TypeError as e:
            boardFound = False
            print("Board not found!"+str(e))

        if not boardFound:
            self.write_label.emit("Board not found")
            self.board_found.emit(False)
        else:
            self.board_found.emit(True)
            self.write_label.emit("")
        self.finished.emit()
            
    def update_bar(self, counter):
        self.progress.emit(counter)
    def update_image(self, img_path):
        self.show_image.emit(img_path)

    def checkbox_change(self, checked):
        if not self.auto_move == checked:
            self.counter = 0
        self.auto_move = checked
        
    def stopped(self):
        self.stopped_bot.emit()
        self.game_stopped = True

class GUI(QMainWindow):

    stopped = pyqtSignal()
    automatic_move_change = pyqtSignal(bool)

    def __init__(self):
        super(GUI, self).__init__()

        self.games_played = 0

        #self.manager = Manager()
        self.started = False
        uic.loadUi("gui/main.ui", self)

        self.show()
        self.set_label_text("")
        self.b_start.setEnabled(False)
        
        self.b_start.clicked.connect(self.start_bot)
        self.b_quit.clicked.connect(self.quit_programm)
        self.b_detect.clicked.connect(self.detect_board)
        self.b_Settings.clicked.connect(self.show_settings)



    def start_bot(self):
        if not self.started:
            if self.games_played > 1:
                time.sleep(2)
            self.games_played += 1
            self.set_label_text("")
            self.started = True
            self.b_Settings.setEnabled(False)
            #self.b_start.setEnabled(False)
            self.b_start.setText("Stop bot")
            self.b_detect.setEnabled(False)
            #self.box_automove.setEnabled(False)
            self.manager = Manager(self, self.checkbox_automove_isChecked(
            ), self.boardCoordinates, self.fieldHeight, self.fieldWidth, self.boardHeight, self.boardWidth)
            self.thread2 = QThread()
            
            self.manager.moveToThread(self.thread2)
            
            self.thread2.started.connect(self.manager.run)
            self.manager.finished.connect(self.thread2.quit)
            self.manager.stopped_bot.connect(self.thread2.quit)
            self.manager.finished.connect(self.manager.deleteLater)
            self.manager.progress.connect(self.manager.deleteLater)
            self.manager.write_label.connect(self.manager.deleteLater)
            self.manager.show_image.connect(self.manager.deleteLater)
            self.thread2.finished.connect(self.thread2.deleteLater)

            self.manager.write_label.connect(self.set_label_text)
            self.manager.progress.connect(self.progressBarUpdate)
            self.manager.show_image.connect(self.show_image)

            self.manager.auto_move_update.connect(self.sent_checkbox_isChecked)
            
                    
            self.thread2.start()

            self.thread2.finished.connect(
                lambda: self.set_label_text("")
            )
            self.thread2.finished.connect(
                lambda: self.progressBarUpdate(0)
            )
            self.manager.finished.connect(
                lambda: self.set_label_text("Game finished")
            )
            
            self.thread2.finished.connect(
                lambda: self.b_detect.setEnabled(True)
            )

            self.thread2.finished.connect(
                lambda: self.b_Settings.setEnabled(True)
            )
            
            self.thread2.finished.connect(
                lambda: self.b_start.setText("Start bot")
            )
            self.manager.stopped_bot.connect(
                lambda: self.show_image('pictures/board_detection.png')
            )
            


        else:
            self.stopped.emit()
            self.started = False
        
            
    def board_found(self, found):
        if found:
            self.b_start.setEnabled(True)

    def detect_board(self):
        self.b_detect.setEnabled(False)
        self.thread = QThread()
        self.manager = Manager(self)
        self.manager.moveToThread(self.thread)
        self.thread.started.connect(self.manager.detect_board)
        self.manager.finished.connect(self.thread.quit)
        self.manager.progress.connect(self.progressBarUpdate)

        self.manager.write_label.connect(self.set_label_text)

        self.manager.show_image.connect(self.show_image)

        self.manager.finished.connect(self.manager.deleteLater)
        self.manager.progress.connect(self.manager.deleteLater)
        self.manager.write_label.connect(self.manager.deleteLater)
        self.manager.show_image.connect(self.manager.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.manager.set_board_coordinates.connect(self.set_boardCoordinates)
        self.manager.set_field_height.connect(self.set_fieldHeight)
        self.manager.set_field_width.connect(self.set_fieldWidth)
        self.manager.set_board_height.connect(self.set_boardHeight)
        self.manager.set_board_width.connect(self.set_boardWidth)
        self.manager.board_found.connect(self.board_found)
        
        self.thread.start()
        self.thread.finished.connect(
            lambda: self.progressBarUpdate(0)
        )
        self.thread.finished.connect(
            lambda: self.b_detect.setEnabled(True)
        )
        self.manager.finished.connect(
            lambda: self.label_board_found.setText("Board detected")
        )
        self.manager.finished.connect(
            lambda: self.label_board_found.setStyleSheet("color: green")
        )

        self.manager.finished.connect(
            lambda: self.b_checkDetection.setEnabled(True)
        )

    def set_boardCoordinates(self, board_coordinates):
        self.boardCoordinates = board_coordinates
    def set_fieldHeight(self, field_h):
        self.fieldHeight = field_h
    def set_fieldWidth(self, field_w):
        self.fieldWidth = field_w
    def set_boardHeight(self, board_h):
        self.boardHeight = board_h
    def set_boardWidth(self, board_w):
        self.boardWidth = board_w

    def show_settings(self):
        pass
        #TODO

    def quit_programm(self):
        exit()

    def show_image(self, img_path):
        try:
            pixmap = QtGui.QPixmap(img_path)
            pixmap = pixmap.scaled(521, 521)
            self.label_image.setPixmap(pixmap)
            self.label_image.show()
        except Exception:
            #self.set_label_text("Error: #410")
            #TODO
            pass
    def clear_image(self):
        self.label_image.clear()
    
    def sent_checkbox_isChecked(self):
        self.automatic_move_change.emit(self.checkbox_automove_isChecked())

    def checkbox_automove_isChecked(self):
        return self.box_automove.isChecked()

    def progressBarUpdate(self, value):
        self.progressBar.setValue(value)

    def set_label_text(self, text):
        self.label_text.setText(text)






def main():
    try:
        app = QApplication([])
        window = GUI()
        app.exec_()
    except Exception as e:
        print(e)

    


