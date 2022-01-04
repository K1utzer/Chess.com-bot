import time
from threading import Thread

import pyautogui
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from .ChessBoard import ChessBoard
from .config import Config
from .ImageDetection import ImageDetection
from .MouseControl import MouseControl
from .StockfishManager import StockfishManager
from .logger import Logger



class Manager(QObject):
    
    finished = pyqtSignal()
    stopped_bot = pyqtSignal()
    
    progress = pyqtSignal(int)
    show_image = pyqtSignal(str)
    write_label = pyqtSignal(str)
    auto_move_update = pyqtSignal()
    board_found = pyqtSignal(bool)

    set_board_coordinates = pyqtSignal(list)
    set_field_height = pyqtSignal(int)
    set_field_width = pyqtSignal(int)
    set_board_height = pyqtSignal(int)
    set_board_width = pyqtSignal(int)


    path = "pictures/"
    game_running = True
    config = Config()
    bar_update_counter = 0
    moves_counter = 0
    auto_move = False
    first_move = True
    game_stopped = False
    
    def __init__(self, parant, logger: Logger, auto_move = None, board_coordinates = None, field_height = None, field_width = None, board_height = None, board_width = None):
        super(Manager, self).__init__()
        
        parant.stopped.connect(self.stopped)
        parant.automatic_move_change.connect(self.checkbox_change)
        
        self.logger = logger
        self.board_coordinates = board_coordinates
        self.field_height = field_height
        self.field_width = field_width
        self.board_height = board_height
        self.board_width = board_width
        self.auto_move = auto_move

    def run(self):
        
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")
        imageDet = ImageDetection(self, self.logger)
        
        self.field_Cords, self.myturn = imageDet.calculate_field_cords(
            self.board_coordinates[0], self.field_height, self.field_width, self)
        chessBoard = ChessBoard()

        try:
            stockfish = StockfishManager(self.config.stockfish_path_name)
        except Exception:
            self.logger.warning(f"Stockfish path wrong")
            self.write_label.emit("Stockfish path \nwrong")
            self.game_stopped = True
        bot_move = None

        while self.game_running and not self.game_stopped:

            tmp_turn = self.myturn

            if chessBoard.getBoard().is_checkmate():
                self.game_running = False
                break
            if self.myturn:
                self.progress.emit(self.bar_update_counter)

                bot_move = self.bot_Turn(stockfish, chessBoard)
            else:

                self.opponent_Turn(bot_move, chessBoard)
            time.sleep(1)
            if not tmp_turn == self.myturn and self.game_running:
                self.show_new_image(f"{self.path}turn_screen.png", imageDet)
                self.moves_counter += 1
            self.auto_move_update.emit()
        if self.game_stopped:
            self.stopped_bot.emit()
        else:
            self.finished.emit()
    
    def show_new_image(self, path_name, imageDet):    
        screenshot = pyautogui.screenshot()
        screenshot.save(path_name)
        imageDet.saveResizedImag(path_name,
            self.board_coordinates[0][0], self.board_coordinates[0][1], self.board_coordinates[0][0]+self.board_width, self.board_coordinates[0][1]+self.board_height)
        self.update_image(path_name)
        
    def bot_Turn(self, stockfish: StockfishManager, chessBoard):
        try:
            best_move = stockfish.get_best_move(chessBoard.getBoard())
        except Exception as e:
            self.logger.error(f"Failed to get stockfish best_move: {e}")
            
        if self.auto_move:
            chessBoard.makeMove(best_move)
            self.write_label.emit(f"Bot move: {best_move}")

            mouseContr = MouseControl()
            try:
                mouseContr.mousePos(
                    self.field_Cords[best_move[:2]][0], self.field_Cords[best_move[:2]][1])
                mouseContr.mouseClick()
                mouseContr.mousePos(
                    self.field_Cords[best_move[2:4]][0], self.field_Cords[best_move[2:4]][1])
                mouseContr.mouseClick()
            except Exception as e:
                self.logger.error(f"Mouse control failed: {e}")
                
            self.myturn = False
        else:
            
            if self.first_move:
                self.write_label.emit(f"Best move: {best_move}")
                imageDet = ImageDetection(self, self.logger)
                screenshot = pyautogui.screenshot()
                screenshot.save(f"{self.path}turn_screen.png")
                half_field_w = int(self.field_width/2)
                half_hield_h = int(self.field_height/2)
                imageDet.draw_rec_on_img(
                    "pictures/turn_screen.png",
                    self.field_Cords[best_move[:2]][0]-half_field_w,
                    self.field_Cords[best_move[:2]][1]-half_hield_h,
                    self.field_Cords[best_move[:2]][0]+half_field_w,
                    self.field_Cords[best_move[:2]][1]+half_hield_h)
                imageDet.draw_rec_on_img(
                    "pictures/turn_screen.png",
                    self.field_Cords[best_move[2:4]][0]-half_field_w,
                    self.field_Cords[best_move[2:4]][1]-half_hield_h,
                    self.field_Cords[best_move[2:4]][0]+half_field_w,
                    self.field_Cords[best_move[2:4]][1]+half_hield_h)
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
        self.bar_update_counter += 2
        if self.bar_update_counter > 98:
            self.bar_update_counter = 2
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
                    #print()
                    #print(f"\Player move: {fmove}{smove}")
                    self.write_label.emit(f"Player move: \n{fmove}{smove}")
                    print(chessBoard.getBoard())
                    self.progress.emit(100)
                    self.bar_update_counter = 0
                    self.first_move = True
                except ValueError:
                    return

    def opponent_Turn(self, bot_move, chessBoard):
        if self.bar_update_counter == 0:
            self.write_label.emit(f"Waiting for\nOpponent move")
        self.bar_update_counter += 2
        if self.bar_update_counter > 98:
            self.bar_update_counter = 2
        self.progress.emit(self.bar_update_counter)
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
                    self.bar_update_counter = 0
                except ValueError:
                    self.logger.error(f"Failed to get opponent move")



    def detect_board(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")

        imageDet = ImageDetection(self, self.logger)

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
            self.logger.warning(f"Board not detected")

        if not boardFound:
            self.write_label.emit("Board not detected\nmake sure that the\nchess board is visible\non your screen")
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
            self.bar_update_counter = 0
        self.auto_move = checked
        
    def stopped(self):
        self.stopped_bot.emit()
        self.game_stopped = True

class GUI(QMainWindow):

    stopped = pyqtSignal()
    automatic_move_change = pyqtSignal(bool)

    def __init__(self):
        super(GUI, self).__init__()

        self.logger = Logger()
        self.games_played = 0

        self.started = False
        uic.loadUi("gui/main.ui", self)

        self.show()
        self.set_label_text("")
        self.b_start.setEnabled(False)
        
        self.b_start.clicked.connect(self.start_bot)
        self.b_quit.clicked.connect(self.quit_programm)
        self.b_detect.clicked.connect(self.detect_board)
        self.b_Settings.clicked.connect(self.show_settings)
        
        self.logger.info(f"Init Main Window")



    def start_bot(self):
        
        if not self.started:
            self.logger.info(f"Started bot. Games played: {self.games_played}")
            
            if self.games_played > 1:
                time.sleep(2)
            self.games_played += 1
            
            
            self.started = True
            self.set_label_text("")
            self.b_Settings.setEnabled(False)
            self.b_start.setText("Stop bot")
            self.b_detect.setEnabled(False)
            
            self.manager = Manager(self, self.logger, self.checkbox_automove_isChecked(
            ), self.boardCoordinates, self.fieldHeight, self.fieldWidth, self.boardHeight, self.boardWidth)
            self.thread = QThread()
            self.manager.moveToThread(self.thread)
            
            self.thread.started.connect(self.manager.run)
            self.manager.finished.connect(self.thread.quit)
            self.manager.stopped_bot.connect(self.thread.quit)
            
            self.manager.write_label.connect(self.set_label_text)
            self.manager.progress.connect(self.progressBarUpdate)
            self.manager.show_image.connect(self.show_image)
            self.manager.auto_move_update.connect(self.sent_checkbox_isChecked)
            
            self.delete_later()        
            self.thread.start()

            self.thread.finished.connect(
                lambda: self.set_label_text("")
            )
            self.manager.finished.connect(
                lambda: self.set_label_text("Game finished")
            )
            self.thread.finished.connect(
                lambda: self.b_Settings.setEnabled(True)
            )
            
            self.thread.finished.connect(
                lambda: self.b_start.setText("Start bot")
            )
            self.manager.stopped_bot.connect(
                lambda: self.show_image('pictures/board_detection.png')
            )
            
            self.at_finish()
            


        else:
            self.logger.info("Stop button pressed")
            self.stopped.emit()
            self.started = False
        
            
    def board_found(self, found):
        if found:
            self.b_start.setEnabled(True)
            self.label_board_found.setText("Board detected")
            self.label_board_found.setStyleSheet("color: green")
            self.b_checkDetection.setEnabled(True)

    def detect_board(self):

        self.b_detect.setEnabled(False)
        
        self.thread = QThread()
        self.manager = Manager(self, self.logger)
        self.manager.moveToThread(self.thread)
        
        self.thread.started.connect(self.manager.detect_board)
        
        self.manager.finished.connect(self.thread.quit)
        self.manager.progress.connect(self.progressBarUpdate)
        self.manager.write_label.connect(self.set_label_text)
        self.manager.show_image.connect(self.show_image)
        
        self.manager.set_board_coordinates.connect(self.set_boardCoordinates)
        self.manager.set_field_height.connect(self.set_fieldHeight)
        self.manager.set_field_width.connect(self.set_fieldWidth)
        self.manager.set_board_height.connect(self.set_boardHeight)
        self.manager.set_board_width.connect(self.set_boardWidth)
        self.manager.board_found.connect(self.board_found)
        
        self.delete_later()
        
        self.thread.start()
        
        self.at_finish()

    def at_finish(self):
        self.thread.finished.connect(
            lambda: self.progressBarUpdate(0)
        )
        self.thread.finished.connect(
            lambda: self.b_detect.setEnabled(True)
        )

        
        
    def delete_later(self):
        self.manager.finished.connect(self.manager.deleteLater)
        self.manager.progress.connect(self.manager.deleteLater)
        self.manager.write_label.connect(self.manager.deleteLater)
        self.manager.show_image.connect(self.manager.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        

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
            self.logger.error("Error displaying image in QLabel=label_image: {e}")

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

    


