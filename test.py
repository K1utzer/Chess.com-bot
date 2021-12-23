
from pyautogui import *
import pyautogui
import time
import keyboard
import random
import win32api
import win32con
import threading

import cv2
import numpy as np

img = cv2.imread("screen_test.JPG")
green = [105,247,248]
X,Y = np.where(np.all(im==green,axis=2))
zipped = np.column_stack((X,Y))

before = True

