import configparser
import chess

import time

import cv2 as cv
import numpy as np

import re
import sys
import os

import random

import pyautogui

import keyboard
import win32api
import win32con

from stockfishpy.stockfishpy import *



class Manager():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.cfg")
        stockfish_path_name = str(self.config.get("stockfish", "path"))
        self.legit = self.config.get("settings", "legit")
        self.keepPlaying = self.config.get("settings", "keepPlaying")
        self.myturn = False
        self.path = "figures/"
        self.board_width = 0
        self.board_height = 0
        self.chessEngine = Engine(stockfish_path_name, param={
                            'Threads': 2, 'Ponder': None})
        self.game_running = True
        self.board = BoardControl()
        self.myturn = self.board.getMyTurn()
        #detect which color -> check if white figures at the bottom, if so -> WHITE
        # dark figures: [82 83 86], white: 248, 248, 248

        # gezogenes feld farbe weiß: R:248,G:247,B:105 grün: R:187,G:203,B:44 -> Zug erkennen von wo wohin
        move = ""
        while self.game_running:
            if self.board.getBoard().is_checkmate():
                print("Game won!" if not self.myturn else "Game lost!")
                exit()
            if self.myturn:
                move = self.botTurn()
            else:
                self.opponentTurn(move)
        
    def botTurn(self):
        # get Stockfish move
        best_move = self.get_best_move(self.chessEngine)
        #print(best_move)
        # write in the python chess libary
        firstField, secondField = self.makeMove(best_move)
        #print(firstField, secondField)
        # click the right coordinates
        #click()
        fields_Cords = self.board.getFieldCords()
        self.click(fields_Cords[firstField][0], fields_Cords[firstField][1])
        time.sleep(random.uniform(0.1, 0.8))
        self.click(fields_Cords[secondField][0], fields_Cords[secondField][1])
        self.myturn = False
        return best_move

        
    def opponentTurn(self, botMove):
        if botMove == None:
            botMove = ""
        # get opponent move: wait if move detected
        print("Waiting for opponent move", end="\r")
        fmove = False
        smove = False
        #opponentMoved = False
        screenshot = pyautogui.screenshot()
        screenshot.save("pictures/turn_screen.png")
        screen = cv.imread("pictures/turn_screen.png")
        field_w = self.board.getFieldWidth()
        field_h = self.board.getFieldHeight()
        field_Cords = self.board.getFieldCords()
        for field in field_Cords:
            x = field_Cords[field][0]
            y = field_Cords[field][1]
            x2 = int(x+(field_w/2)-10)
            y2 = int(y-(field_h/2)+10)
            if (screen[y2, x2][0] <= 115 and
                screen[y2, x2][1] >= 235 and
                screen[y2, x2][2] >= 235):
                yellow_white = [screen[y2, x2][0], screen[y2, x2][1], screen[y2, x2][2]]
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
                yellow_green = [screen[y2, x2][0], screen[y2, x2][1], screen[y2, x2][2]]
                if list(screen[y+10, x]) == yellow_green:
                    fmove = field
                else:
                    smove = field
                    #opponentMoved = True
        if fmove and smove and str(fmove+smove) not in botMove:
            try:
                self.board.makeMove(f"{fmove}{smove}")
                self.myturn = True
                print()
                print(f"\nOpponent move: {fmove}{smove}")
                print(self.board.getBoard())
            except ValueError:
                time.sleep(1)
                return

        # write it in python chess libary
         # gezogenes feld farbe weiß: R:248,G:247,B:105 
         # grün: R:187,G:203,B:44 -> Zug erkennen von wo wohin
        
    def get_best_move(self, chessEngine):

        chessEngine.ucinewgame()
        chessEngine.setposition(self.board.getBoard().fen())

        move = chessEngine.bestmove()
        bestmove = move['bestmove']

        return bestmove


    def makeMove(self, best_move):
        #print(best_move)
        #moveTmp = chess.Move.from_uci(best_move)
        #board.push(moveTmp)
        self.board.makeMove(best_move)

        print(f"\nMy Move: {best_move}")
        print(self.board.getBoard())
        return best_move[:2], best_move[2:4]

    def click(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(random.uniform(0.01, 0.2))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        #win32api.SetCursorPos(
            #(random.uniform(1, 1080), random.uniform(1, 720)))
        

class ImageDet:

    def searchBoard(self, screenshot, board_layout1, board_layout2):

        """
        Search board on screen, rescale if not found (100x times)

        Returns:
            [[(int),(int)], int, int , int, int]: Boad coordinates left, upper corner and right lower corner x and y,
                                                single field height, single field width, board height, board width
        """
        maxValue1 = 0
        maxValue2 = 0
        dots = "."
        threshold = 0.8 
        print("Searching board", end="\r")
        for c in range(100):
            print(f"Searching board {dots*c}", end="\r")
            board_result1 = cv.matchTemplate(
                screenshot, board_layout1, cv.TM_CCOEFF_NORMED)
            board_result2 = cv.matchTemplate(
                screenshot, board_layout2, cv.TM_CCOEFF_NORMED)
        #cv.imshow('image', screenimg)
        #cv.imshow('image', board)
            min_val1, max_val1, min_loc1, max_loc1 = cv.minMaxLoc(board_result1)
            min_val2, max_val2, min_loc2, max_loc2 = cv.minMaxLoc(board_result2)
            if max_val1 > maxValue1:
                maxValue1 = max_val1
                maxLoc1 = max_loc1
                board_w1 = board_layout1.shape[1]
                board_h1 = board_layout1.shape[0]
            if max_val2 > maxValue2:
                maxValue2 = max_val2
                maxLoc2 = max_loc2
                board_w2 = board_layout2.shape[1]
                board_h2 = board_layout2.shape[0]
            width1 = int(board_layout1.shape[1] * 99/100)
            higth1 = int(board_layout1.shape[0] * 99/100)
            width2 = int(board_layout2.shape[1] * 99/100)
            higth2 = int(board_layout2.shape[0] * 99/100)
            board_layout1 = cv.resize(board_layout1, (width1, higth1))
            board_layout2 = cv.resize(board_layout2, (width2, higth2))
            os.system("cls")
            if maxValue1 >= threshold:
                print("Board found")
                return True, [max_loc1, (int(max_loc1[0]+board_w1/8), int(max_loc1[1]+board_h1/8))], board_h1/8, board_w1/8,  board_h1, board_w1
            if maxValue2 >= threshold:
                return False, [max_loc2, (int(max_loc2[0]+board_w2/8), int(max_loc2[1]+board_h2/8))], board_h2/8, board_w2/8,  board_h2, board_w2
        exit()
        

class BoardControl:
    
    def __init__(self):
        
        self.myTurn = True
        self.path = "pictures/"
        self.imageDet = ImageDet()
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")
        screenshot = cv.imread(f"{self.path}screen.png", cv.IMREAD_UNCHANGED)
        
        try:
            self.myTurn, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width = self.imageDet.searchBoard(
                screenshot, cv.imread(f"{self.path}layout1.PNG"), cv.rotate(cv.imread(f"{self.path}layout1.PNG"), cv.ROTATE_180))
        except TypeError as e:
            print("Board not found!")
            exit()
            
        self.fields_Cords = self.field_cords(self.board_coordinates[0], self.field_height, self.field_width, screenshot)
        self.board = chess.Board()

    def getMyTurn(self):
        return self.myTurn

    def getBoard(self):
        return self.board  

    def getFieldCords(self):
        return self.fields_Cords

    def getFieldWidth(self):
        return self.field_width
    def getFieldHeight(self):
        return self.field_height

    def makeMove(self, move):
        self.board.push_san(move)

    def field_cords(self, top_left, field_h, field_w, screenimg):
        
        bottom_right = (int(top_left[0]+field_w), int(top_left[1]+field_h))
        start_X = top_left[0]
        #start_Y = top_left[1]
        firstX = True
        firstY = True
        fields_Cords = {}
        abc = "abcdefgh"
        oneTwothree = "87654321"
        if not self.myTurn:
            oneTwothree = "12345678"
            abc = "hgfedcba"
        for c in range(8):
            firstX = True
            if not firstY:
                tmp = list(top_left)
                tmp[1] = int(tmp[1]+field_h)
                tmp[0] = int(start_X)
                top_left = tuple(tmp)
            else:
                firstY = False
            for c1 in range(8):
                if not firstX:
                    tmp = list(top_left)
                    tmp[0] = int(tmp[0]+field_w)
                    top_left = tuple(tmp)
                    bottom_right = (int(top_left[0]+field_w), int(top_left[1]+field_h))

                else:
                    firstX = False
                #fields_Cords.append([int(top_left[0] + ( field_w / 2 )), int( top_left[1] + ( field_h / 2 ))])
                fields_Cords.update(
                    {str(abc[c1]+oneTwothree[c]): [int(top_left[0] + (field_w / 2)), int(top_left[1] + (field_h / 2))]})
                cv.rectangle(screenimg, top_left, bottom_right, color=(
                    0, 255, 0), thickness=2, lineType=cv.LINE_4)

        for key, c in fields_Cords.items():
            #print(key, c)
            cv.circle(screenimg, tuple(c), 5, color=(0, 0, 255))
            cv.putText(screenimg, str(key), tuple(
                c), cv.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=2, color=(142, 142, 142))
        #cv.imshow('Result', screenimg)
        cv.imwrite("board_result.jpg", screenimg)
        #cv.waitKey()
        #print(fields_Cords)
        return fields_Cords


if sys.version_info[0] < 3:
    raise Exception("Must be using Python version 3. Developed with Python 3.8.8")
if sys.version_info[1] != 8:
    print("WARNING: Developed with Python version 3.8.8. May not work properly if used with another version")
elif sys.version_info[2] != 8:
    print("WARNING: Developed with Python version 3.8.8. May not work properly if used with another version")

manager = Manager()
