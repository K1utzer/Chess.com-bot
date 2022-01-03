import chess.engine

class StockfishManager:

    def __init__(self, stockfish_path_name):
        try:
            
            self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path_name)
        except Exception as e:
            print(e)

    def get_best_move(self, board):

        result = self.engine.play(board, chess.engine.Limit(time=0.1))
        return str(result.move)
