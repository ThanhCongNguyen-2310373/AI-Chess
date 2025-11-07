"""
Base class cho tất cả các agents
"""
import chess


class BaseAgent:
    """Lớp cơ sở cho tất cả các AI agents"""
    
    def __init__(self, name="BaseAgent"):
        self.name = name
        self.nodes_searched = 0  # Số node đã duyệt
    
    def get_move(self, board):
        """
        Chọn nước đi tiếp theo
        
        Args:
            board: Bàn cờ hiện tại (chess.Board)
        
        Returns:
            chess.Move: Nước đi được chọn
        """
        raise NotImplementedError("Subclass must implement get_move method")
    
    def reset_stats(self):
        """Reset thống kê"""
        self.nodes_searched = 0
    
    def get_stats(self):
        """Lấy thông tin thống kê"""
        return {
            'name': self.name,
            'nodes_searched': self.nodes_searched
        }
