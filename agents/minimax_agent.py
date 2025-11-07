"""
Agent sử dụng thuật toán Minimax với Alpha-Beta Pruning
"""
import chess
from .base_agent import BaseAgent
from utils import get_piece_value, get_position_value, is_endgame
from config import MINIMAX_DEPTH


class MinimaxAgent(BaseAgent):
    """Agent sử dụng Minimax với Alpha-Beta Pruning"""
    
    def __init__(self, depth=MINIMAX_DEPTH):
        super().__init__(name="Minimax Agent")
        self.depth = depth
    
    def evaluate_board(self, board):
        """
        Hàm đánh giá bàn cờ
        
        Args:
            board: Bàn cờ cần đánh giá
        
        Returns:
            Điểm số (dương = trắng lợi thế, âm = đen lợi thế)
        """
        # Kiểm tra trạng thái kết thúc
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -999999  # Đen thắng
            else:
                return 999999   # Trắng thắng
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Hòa
        
        score = 0
        endgame = is_endgame(board)
        
        # Đánh giá từng quân cờ
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Giá trị quân cờ
                piece_value = get_piece_value(piece)
                
                # Giá trị vị trí
                position_value = get_position_value(piece, square, endgame)
                
                total_value = piece_value + position_value
                
                # Cộng điểm cho trắng, trừ điểm cho đen
                if piece.color == chess.WHITE:
                    score += total_value
                else:
                    score -= total_value
        
        # Thưởng cho khả năng di chuyển (mobility)
        if board.turn == chess.WHITE:
            score += len(list(board.legal_moves)) * 10
        else:
            score -= len(list(board.legal_moves)) * 10
        
        # Phạt nếu bị chiếu
        if board.is_check():
            if board.turn == chess.WHITE:
                score -= 50
            else:
                score += 50
        
        return score
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Thuật toán Minimax với Alpha-Beta Pruning
        
        Args:
            board: Bàn cờ hiện tại
            depth: Độ sâu còn lại
            alpha: Giá trị alpha cho pruning
            beta: Giá trị beta cho pruning
            maximizing_player: True nếu đang tối đa hóa, False nếu tối thiểu hóa
        
        Returns:
            Điểm số tốt nhất
        """
        self.nodes_searched += 1
        
        # Điều kiện dừng
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
    
    def get_move(self, board):
        """
        Tìm nước đi tốt nhất bằng Minimax
        
        Args:
            board: Bàn cờ hiện tại
        
        Returns:
            Nước đi tốt nhất
        """
        self.reset_stats()
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Duyệt qua tất cả nước đi hợp lệ
        for move in legal_moves:
            board.push(move)
            
            # Gọi minimax để đánh giá
            if board.turn == chess.BLACK:  # Sau khi đi, đến lượt đen
                # Trắng vừa đi, tìm max
                move_value = self.minimax(board, self.depth - 1, alpha, beta, False)
            else:  # Sau khi đi, đến lượt trắng
                # Đen vừa đi, tìm min
                move_value = self.minimax(board, self.depth - 1, alpha, beta, True)
            
            board.pop()
            
            # Cập nhật nước đi tốt nhất
            if board.turn == chess.WHITE:
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
                    alpha = max(alpha, move_value)
            else:
                if move_value < best_value:
                    best_value = move_value
                    best_move = move
                    beta = min(beta, move_value)
        
        return best_move
