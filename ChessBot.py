import configparser
import chess

import time

import cv2 as cv
import numpy as np

import re

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
        self.stockfish_path_name = str(self.config.get("stockfish", "path"))
        self.legit = self.config.get("settings", "legit")
        self.keepPlaying = self.config.get("settings", "keepPlaying")
        self.myturn = False
        self.path = "figures/"
        self.board_width = 0
        self.board.height = 0
        #detect which color -> check if white figures at the bottom, if so -> WHITE
        
        


class ImageDet:

    def searchBoard(self, screenshot, board_layout):
        maxValue = 0
        dots = "."
        threshold = 0.65
        print("Searching board", end="\r")
        for c in range(int(maxValue+10)):
            print(f"Searching board {dots*c}", end="\r")
            board_result = cv.matchTemplate(
                screenshot, board_layout, cv.TM_CCOEFF_NORMED)
        #cv.imshow('image', screenimg)
        #cv.imshow('image', board)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(board_result)
            if max_val > maxValue:
                maxValue = max_val
                maxLoc = max_loc
                board_w = board_layout1.shape[1]
                board_h = board_layout1.shape[0]
                if maxValue >= threshold:
                    break
            width = int(board_layout.shape[1] * 90/100)
            higth = int(board_layout.shape[0] * 90/100)
            board_layout1 = cv.resize(board_layout, (width, higth))
        if maxValue >= threshold:
            print("Found board")
            return [max_loc, (int(max_loc[0]+board_w/8), int(max_loc[1]+board_h/8))], board_h/8, board_w/8,  board_h, board_w

class Board:
    
    def __init__(self):
        self.path = "figures/"
        self.imageDet = ImageDet()
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")
        screenshot = cv.imread(f"{self.path}screen.png", cv.IMREAD_UNCHANGED)
        
        self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width = self.imageDet.searchBoard(
            screenshot, cv.imread(f"{self.path}layout1.PNG"))
        
        self.field_Cords = self.field_cords(self.board_coordinates[0], self.field_height, self.field_width, screenshot)
        
        self.board = chess.Board()
        
    def field_cords(self, top_left, field_h, field_w, screenimg):
        
        start_X = top_left[0]
        start_Y = top_left[1]
        firstX = True
        firstY = True
        fields_Cords = {}
        abc = "abcdefgh"
        oneTwothree = "87654321"
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
                    bottom_right = (
                        int(top_left[0]+field_w), int(top_left[1]+field_h))
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
                c), cv.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=2, color=(255, 255, 255))
        #cv.imshow('Result', screenimg)
        cv.imwrite("board_result.jpg", screenimg)
        #cv.waitKey()
        #print(fields_Cords)
        return fields_Cords
