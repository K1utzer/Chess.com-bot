from stockfishpy.stockfishpy import *

class StockfishManager:

    def __init__(self, stockfish_path_name):
        self.chessEngine = Engine(stockfish_path_name, param={
            'Threads': 2, 'Ponder': None})

    def get_best_move(self, board):
        self.chessEngine.ucinewgame()
        self.chessEngine.setposition(board.fen())
        return self.chessEngine.bestmove()['bestmove']