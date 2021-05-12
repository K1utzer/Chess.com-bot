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
import win32api, win32con

from stockfishpy.stockfishpy import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException


config = configparser.ConfigParser()
config.read("config.cfg")
stockfish_path_name = str(config.get("stockfish", "path_name"))
username = str(config.get("chess.com", "username"))
password = str(config.get("chess.com", "password"))
legit = bool(config.get("settings", "legit"))
keepPlaying = bool(config.get("settings", "keepPlaying"))
movesCounter = 0
myturn = False
fields_Cords = {}
alwaysPrint = ""
pauseMaxTime = 0

gameOverMessageCount = 0


def login(driver):
    global username, password
    elem = driver.find_element_by_id('username')
    elem.clear()
    elem.send_keys(username)
    elem = driver.find_element_by_id('password')
    elem.clear()
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    return

def load_page():
    driver = webdriver.Firefox()
    driver.get('https://www.chess.com/login')
    return driver

def get_user_color(driver):
    dot = "."
    minus = False
    
    print(f"Waiting for user to start new game", end="   \r")
    while (1):
        try:
            myElem = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'draw-button-component')))
            elem_list = driver.find_elements_by_class_name("live-game-start-component")
            if('warn-message-component' in elem_list[-1].get_attribute('class')):
                elem = elem_list[-2]
            else:
                elem = elem_list[-1]
            break
        except TimeoutException:
            print(f"Waiting for user to start new game{dot}", end="   \r")
            
            if len(dot) > 2:
                minus = True
            elif len(dot) == 0:
                minus = False
            if minus:
                dot = dot[:-1]
            else:
                dot += "."


    global alwaysPrint, pauseMaxTime, legit
    alwaysPrint = elem.text
    pattern = re.compile("(\d{1,2} \| \d{1,2})")
    gameModeTimes = re.findall('[0-9]+', pattern.search(elem.text).group())
    if int(gameModeTimes[0]) < 3:
        pauseMaxTime = 13.0
    elif int(gameModeTimes[0]) < 5:
        pauseMaxTime = 25.0
    elif int(gameModeTimes[0]) < 10:
        pauseMaxTime = 50.0
    elif int(gameModeTimes[0]) >= 15:
        pauseMaxTime = 90.0
    if not legit:
        pauseMaxTime = 0
    print(elem.text)
    players = re.findall(r'(\w+)\s\(\d+\)', elem.text)

    white_player = players[0]

    global username

    if white_player == username:
        print(username + ' is white')
        return "white"
    else:
        print(username + ' is black')
        return "black"

def getBoard():
    try:
        
        path = "figures/"

        screenshot = pyautogui.screenshot()
        screenshot.save(f"{path}screen.png")
        board_layout1 = cv.imread(f"{path}layout1.PNG")
        nextGame = cv.imread(f"{path}nextGame.png")
        screenimg = cv.imread(f"{path}screen.png", cv.IMREAD_UNCHANGED)
        maxValue = 0
        dots = "."
        threshold = 0.5
        print("Searching board", end="\r")
        for c in range(int(maxValue+10)):
            print(f"Searching board {dots*c}", end="\r")
            board_result = cv.matchTemplate(screenimg, board_layout1, cv.TM_CCOEFF_NORMED)
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
            width = int(board_layout1.shape[1] * 90/100)
            higth = int(board_layout1.shape[0] * 90/100)
            board_layout1 = cv.resize(board_layout1, (width, higth))
        

        if maxValue >= threshold:
            
            print("Found board")            
            
            top_left = maxLoc
            #bottom_right = (top_left[0] + board_w, top_left[1] + board_h)
            #cv.rectangle(screenimg, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
            
            #bottom_right = (int(top_left[0] + board_w/8), int(top_left[1] + board_h/8))
            
            field_w = board_w/8
            field_h = board_h/8

            bottom_right = (int(top_left[0]+field_w), int(top_left[1]+field_h))
            #cv.rectangle(screenimg, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
            start_X = top_left[0]
            start_Y = top_left[1]
            firstX = True
            firstY = True
            global fields_Cords
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
                        bottom_right = (int(top_left[0]+field_w), int(top_left[1]+field_h))
                    else:
                        firstX = False
                    #fields_Cords.append([int(top_left[0] + ( field_w / 2 )), int( top_left[1] + ( field_h / 2 ))])
                    fields_Cords.update({str(abc[c1]+oneTwothree[c]): [int(top_left[0] + ( field_w / 2 )), int( top_left[1] + ( field_h / 2 ))]})
                    cv.rectangle(screenimg, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)  

            for key, c in fields_Cords.items():
                #print(key, c)
                cv.circle(screenimg, tuple(c), 5, color=(0,0,255))
                cv.putText(screenimg, str(key), tuple(c), cv.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=2, color=(255,255,255))
            #cv.imshow('Result', screenimg)
            cv.imwrite("board_result.jpg", screenimg)
            #cv.waitKey()  
            #print(fields_Cords)            
        else:
            print("Board not found")
            return False
    except Exception as e:
        #print(f"Error occured. Will try again. {e}")
        raise e
        return False
    return True
def get_best_move(chessEngine, board):

    chessEngine.ucinewgame()
    chessEngine.setposition(board.fen())

    move = chessEngine.bestmove()
    bestmove = move['bestmove']

    return bestmove

def float_to_string(number, precision):
	if not precision:
		precision = 2
	return '{0:.{prec}f}'.format(number, prec=precision,).rstrip('0').rstrip('.') or '0'
    
def run_game(driver, chessEngine, board):
    #zug = input('Zieh nun: ')
    #zug = board.push_san(zug)
    global movesCounter
    global myturn
    global gameOverMessageCount
    global alwaysPrint, pauseMaxTime
    if myturn:
        game_ended = game_end(driver, gameOverMessageCount)
        if game_ended:
            os.system('cls')
            print(f'{alwaysPrint}\nGame finished!')
            return False
        pauseTime = 0
        if movesCounter > 12:
            pauseTime = random.uniform(0.5, pauseMaxTime)
        best_move = get_best_move(chessEngine, board)
        os.system('cls')
        print(f"{alwaysPrint}\nMy Turn")

        print(f"Pause: {float_to_string(pauseTime, 2)}s", end="\r")
        rest = pauseTime - int(pauseTime)
        for _ in range(int(pauseTime)):
            if keyboard.is_pressed('s'):
                break
            time.sleep(1)   
        time.sleep(rest)
        #print(f"My Move: {best_move}")
        #time.sleep(pauseTime)
        #print(board, best_move)
        makeMove(board, best_move)
        #board.push_san(best_move)
        print(board)
        myturn = False

        return True
    else:
        try:
            print("Enemy turn", end="\r")
            game_ended = game_end(driver, gameOverMessageCount)
            if game_ended:
                os.system('cls')
                print(f'{alwaysPrint}\nGame finished!')
                return False
            board = getMoves(board, driver)
            if board != False:
                myturn = True
                movesCounter += 1
            elif board == "end":
                return False
        except StaleElementReferenceException:
            return False
        return True
def getMoves(board, driver):
    #<div class="move" data-whole-move-number="1">1.<div data-ply="1" class="white node">e4</div><div data-ply="1" data-vml-element="timestamp" class="time-white" data-time="1" style="--timeValue:1; --timeBarWidth:0.06130408137820751px;">0.1</div><div data-ply="2" class="black node">c6</div><div data-ply="2" data-vml-element="timestamp" class="time-black" data-time="3" style="--timeValue:3; --timeBarWidth:0.18391116775261646px;">0.3</div></div>
    global movesCounter
    element = driver.find_elements(By.CLASS_NAME, 'move')
    moves = []
    for c in element:
        tmp = c.text.split("\n")
        for c2 in range(len(tmp)):
            if c2 == 1 or c2 == 3:
                moves.append(tmp[c2])

    #print(moves)
    if len(moves) <= movesCounter:
        return False
    try:
        print("Enemy turn")
        print(f"Enemy Move: {str(moves[len(moves)-1])}")
        zug = board.push_san(str(moves[len(moves)-1]))
        print(board)
    except Exception as e:
        if "invalid san" in str(e):
            return "end"
    return board

def click(x, y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(random.uniform(0.01, 0.2))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    
def makeMove(board, best_move):
    #print(best_move)
    global movesCounter 
    global fields_Cords
    moveTmp = chess.Move.from_uci(best_move)
    board.push(moveTmp)
    print(f"My Move: {moveTmp}")
    movesCounter += 1
    firstField = ""
    secondField = ""
    first = True
    for c in best_move:
        #print("c: "+str(c))
        if first:
            try:
                tmp = int(c)
                firstField = firstField+str(c)
                first = False
            except Exception:
                firstField = firstField+str(c)
        else:
            try:
                tmp = int(c)
                secondField = secondField+str(c)
                break
            except Exception:
                secondField = secondField+str(c)
    #print(firstField, secondField)
    click(fields_Cords[firstField][0], fields_Cords[firstField][1])
    time.sleep(random.uniform(0.1, 0.8))
    click(fields_Cords[secondField][0], fields_Cords[secondField][1])
def game_end(driver, gameOverMessageCount):
    game_finished_message = 0

    gameOverMessageCountNew = 0
    

    elements = driver.find_elements_by_class_name('live-game-over-component')
    gameOverMessageCountNew = len(elements)
            
    if gameOverMessageCountNew > gameOverMessageCount:
        game_finished_message = 1
        
    return game_finished_message


#pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\wolf-\\AppData\\Local\\Tesseract-OCR\\tesseract.exe"
# pic = pyautogui.screenshot(region=(1242,751,150,50))
# pic.save('screen.png')
# img = cv2.imread('screen.png')
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# print(pytesseract.image_to_string(img))
# cv2.imshow('Result', img)
# cv2.waitKey(0)

def checkGameState(driver):
    global movesCounter
    global myturn
    element = driver.find_elements(By.CLASS_NAME, 'move')
    moves = []
    for c in element:
        tmp = c.text.split("\n")
        for c2 in range(len(tmp)):
            if c2 == 1 or c2 == 3:
                moves.append(tmp[c2])

    #print(moves)
    board = chess.Board()
    for c in moves:
        movesCounter += 1
        if myturn:
            myturn = False
        else:
            myturn = True
        #print("Moves: "+str(c))
        zug = board.push_san(c)
        print(board)
    return board

def startPage():
    driver = load_page()
    login(driver)
    return driver
def init():
    global stockfish_path_name
    chessEngine = Engine(stockfish_path_name, param={'Threads': 10, 'Ponder': None})
    board = chess.Board()
    return chessEngine, board
def restart():
    path = "figures/"
    print("Next game")
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{path}screen.png")
        nextGame = cv.imread(f"{path}nextGame.png")
        screenimg = cv.imread(f"{path}screen.png", cv.IMREAD_UNCHANGED)
        maxValue = 0
        dots = "."
        threshold = 0.8
        print("Searching new game button", end="\r")
        for c in range(int(maxValue+10)):
            print(f"Searching new game button {dots*c}", end="\r")
            board_result = cv.matchTemplate(screenimg, nextGame, cv.TM_CCOEFF_NORMED)
        #cv.imshow('image', screenimg)
        #cv.imshow('image', board)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(board_result)
            if max_val >= threshold:
                maxValue = max_val
                maxLoc = max_loc
                board_w = nextGame.shape[1]
                board_h = nextGame.shape[0]
                if maxValue >= threshold:
                    break 
            width = int(nextGame.shape[1] * 90/100)
            higth = int(nextGame.shape[0] * 90/100)
            board_layout1 = cv.resize(nextGame, (width, higth))
        if maxValue >= threshold:
            
            print("Found next game button")            
                
            top_left = maxLoc
                #bottom_right = (top_left[0] + board_w, top_left[1] + board_h)
                #cv.rectangle(screenimg, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
                
                #bottom_right = (int(top_left[0] + board_w/8), int(top_left[1] + board_h/8))
                
            field_w = board_w/8
            field_h = board_h/8

            bottom_right = (int(top_left[0]+field_w), int(top_left[1]+field_h))
            #cv.rectangle(screenimg, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)  
            cv.circle(screenimg, top_left, 5, color=(0,0,255))
            #cv.imshow('Result', screenimg)
            #cv.imwrite("board_result.jpg", screenimg)
            click(top_left[0], top_left[1])
        else:
            print("Next game button not found")
    except Exception as e:
        print(e)
def main(driver, chessEngine, board, newBoard):
    playerColor = get_user_color(driver)
    if newBoard:
        while not getBoard():
            time.sleep(0.1)
    if playerColor == 'white':
        global myturn
        myturn = True
        board = checkGameState(driver)
    while run_game(driver, chessEngine, board):
        time.sleep(0.5)
    global keepPlaying
    if keepPlaying:
        for _ in range(20):
            if keyboard.is_pressed('q'):
                quit()
            time.sleep(1)
        restart()
    print()
    start(driver)
def start(driver):
    global movesCounter
    movesCounter = 0
    global myturn
    myturn = False
    global fields_Cords
    newBoard = True
    if fields_Cords:
        newBoard = False
    global gameOverMessageCount
    elements = driver.find_elements_by_class_name('live-game-over-component')
    gameOverMessageCount = len(elements)
    chessEngine, board = init()
    main(driver, chessEngine, board, newBoard)
if __name__ == '__main__':
    start(startPage())
    
