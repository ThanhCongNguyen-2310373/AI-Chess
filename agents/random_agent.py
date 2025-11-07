"""
Agent chơi ngẫu nhiên (baseline để đánh giá)
"""
import random
import chess
from .base_agent import BaseAgent


class RandomAgent(BaseAgent):
    """Agent chọn nước đi ngẫu nhiên từ các nước đi hợp lệ"""
    
    def __init__(self):
        super().__init__(name="Random Agent")
    
    def get_move(self, board):
        """
        Chọn một nước đi ngẫu nhiên từ các nước đi hợp lệ
        
        Args:
            board: Bàn cờ hiện tại
        
        Returns:
            Nước đi ngẫu nhiên
        """
        legal_moves = list(board.legal_moves)
        
        if not legal_moves:
            return None
        
        return random.choice(legal_moves)
