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
        
        #detect which color -> check if white figures at the bottom, if so -> WHITE
        

def pictureDetection(imgIn, imgToSearch):
    pass
    #return coordinates, field_length, field_width, board_width, board_length

class Board:
    
    def __init__(self):
        board = chess.Board()
