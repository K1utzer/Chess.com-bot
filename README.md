# Chess.com bot

The bot plays on chess.com for you.

It uses the Stockfish13 engine and image detection (opencv)

Download Stockfish engine [here](https://stockfishchess.org/) and add it to the stockfish folder.

[Youtube video](https://youtu.be/17iM9LtQpU0) of the bot is playing



**You have to do some settings on chess.com:**
* Always Promote to Queen
* language: english


### Board detection:
![Board result](/board_detection.PNG)


## Install libaries

```
pip install -r requirements.txt
```



## Config

* stockfish_path_name: the path to the stockfish .exe9
* legit: the bot takes random pauses to look legit (not included yet)
* keepPlaying: the bot will search for next game, if the recent is finished (not included yet)

## Play

Start a game on chess.com

start bot and have your browser visible (the chess.com page):
```
python bot.py
```
## Warning

**The use of external software is forbidden on chess.com.**

**I don't recommend using this bot, because you probably get banned.**

**Use on own responsibility.**
