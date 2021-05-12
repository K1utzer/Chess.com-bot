# Chess.com bot

The bot plays on chess.com for you
It uses the Stockfish13 engine, webscraping and picture detection (opencv)

if ```legit=True``` the random time for you moves:
    - < 3 minutes: pause: 0-13s
    - < 5 minutes: pause: 0-25s
    - < 10 minutes: pause: 0-50s
    - < 15 minutes: pause: 0-90s
if ```legit=False``` the bot will take no pause

![Board result](/board_result.png)
Format: ![board_result](url)


## Install

```
pip install -r requirements.txt
```

## Controls

You can skip the break by pressing 's'


## Config

chess.com: username and passwort
stockfish_path_name: the path to the stockfish .exe
legit: the bot takes random pause to look legit
keepPlaying: the bot will search for next game, if the recent is finished

## Play

The browser (which opened) must be always visible on screen

start bot:
```
python bot.py
```
## Statistic

Winrate 100%, probably lower on higher ranks
Banrate 100%, 2 Accounts - 2 Banned

**The use from external software is forbidden on chess.com**
**I don't recommend using this bot, because you probably get banned.**
**Use on own responsibility.**
