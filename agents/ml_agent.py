"""
Agent sử dụng Machine Learning (Neural Network)
"""
import chess
import numpy as np
import os
from .base_agent import BaseAgent
from utils import fen_to_tensor, get_piece_value
from config import ML_DEPTH, ML_MODEL_PATH


class MLAgent(BaseAgent):
    """Agent sử dụng mô hình ML để đánh giá bàn cờ"""
    
    def __init__(self, model_path=ML_MODEL_PATH, depth=ML_DEPTH):
        super().__init__(name="ML Agent")
        self.depth = depth
        self.model = None
        self.model_path = model_path
        self._evaluation_cache = {}  # Cache để tăng tốc
        
        # De-normalization parameters (LƯU Ý: Cần load từ file hoặc set từ training)
        # Giá trị mặc định tạm thời (NẾU không có file normalization_params.npy)
        self.y_mean = 0.0
        self.y_std = 1000.0  # Giá trị ước lượng
        
        self._load_model()
        self._load_normalization_params()
    
    def _load_model(self):
        """Tải model đã train"""
        try:
            import tensorflow as tf
            # Load với compile=False để tránh lỗi deserialize metrics
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            print(f"✓ Đã tải model từ {self.model_path}")
        except Exception as e:
            print(f"✗ Không thể tải model: {e}")
            print("  Agent sẽ sử dụng đánh giá ngẫu nhiên")
            self.model = None
    
    def _load_normalization_params(self):
        """Tải parameters để de-normalize (y_mean, y_std)"""
        # Tìm file normalization_params.npy cùng thư mục với model
        model_dir = os.path.dirname(self.model_path)
        params_path = os.path.join(model_dir, 'normalization_params.npy')
        
        try:
            if os.path.exists(params_path):
                params = np.load(params_path)
                self.y_mean = float(params[0])
                self.y_std = float(params[1])
                print(f"✓ Đã tải normalization params: mean={self.y_mean:.2f}, std={self.y_std:.2f}")
            else:
                print(f"⚠ Không tìm thấy {params_path}")
                print(f"  Sử dụng giá trị mặc định: mean={self.y_mean:.2f}, std={self.y_std:.2f}")
                print(f"  Để tạo file này, chạy lại training và lưu np.array([y_mean, y_std])")
        except Exception as e:
            print(f"⚠ Lỗi khi load normalization params: {e}")
            print(f"  Sử dụng giá trị mặc định")
    
    def evaluate_board(self, board):
        """
        Đánh giá bàn cờ bằng ML model (với cache)
        
        Args:
            board: Bàn cờ cần đánh giá
        
        Returns:
            Điểm số từ model
        """
        if self.model is None:
            # Fallback: trả về điểm ngẫu nhiên nếu không có model
            return np.random.uniform(-100, 100)
        
        # Kiểm tra game over
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -999999
            else:
                return 999999
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        # Sử dụng FEN làm cache key
        fen = board.fen()
        if fen in self._evaluation_cache:
            return self._evaluation_cache[fen]
        
        # Chuyển board -> FEN -> Tensor
        tensor = fen_to_tensor(fen)
        
        # Thêm batch dimension
        tensor_batch = np.expand_dims(tensor, axis=0)
        
        # Dự đoán
        try:
            score_normalized = self.model.predict(tensor_batch, verbose=0)[0][0]
            
            # DE-NORMALIZE: Chuyển từ normalized score về actual score
            score_actual = float(score_normalized * self.y_std + self.y_mean)
            
            # Lưu vào cache
            self._evaluation_cache[fen] = score_actual
            return score_actual
        except Exception as e:
            print(f"Lỗi khi predict: {e}")
            return 0.0
    
    def order_moves(self, board, moves):
        """
        Sắp xếp nước đi theo thứ tự ưu tiên (MVV-LVA + Checks)
        Giúp alpha-beta pruning hiệu quả hơn
        
        Args:
            board: Bàn cờ hiện tại
            moves: Danh sách nước đi cần sắp xếp
        
        Returns:
            Danh sách nước đi đã sắp xếp
        """
        def move_priority(move):
            priority = 0
            
            # 1. Captures (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
            if board.is_capture(move):
                # Quân bị bắt
                victim = board.piece_at(move.to_square)
                if victim:
                    victim_value = get_piece_value(victim)
                    priority += victim_value * 10
                
                # Quân tấn công
                attacker = board.piece_at(move.from_square)
                if attacker:
                    attacker_value = get_piece_value(attacker)
                    priority -= attacker_value  # Quân nhỏ bắt quân lớn = tốt hơn
            
            # 2. Promotions
            if move.promotion:
                priority += 9000  # Rất cao
            
            # 3. Checks
            board.push(move)
            if board.is_check():
                priority += 50
            board.pop()
            
            return priority
        
        # Sắp xếp theo priority giảm dần
        return sorted(moves, key=move_priority, reverse=True)
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Minimax với ML evaluation
        
        Args:
            board: Bàn cờ hiện tại
            depth: Độ sâu còn lại
            alpha: Alpha value
            beta: Beta value
            maximizing_player: True nếu maximizing
        
        Returns:
            Điểm số
        """
        self.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)
        
        # Sắp xếp nước đi để cải thiện pruning
        legal_moves = list(board.legal_moves)
        ordered_moves = self.order_moves(board, legal_moves)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in ordered_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def get_move(self, board):
        """
        Tìm nước đi tốt nhất bằng Minimax + ML
        
        Args:
            board: Bàn cờ hiện tại
        
        Returns:
            Nước đi tốt nhất
        """
        self.reset_stats()
        
        # Clear cache nếu quá lớn (giữ tối đa 1000 positions)
        if len(self._evaluation_cache) > 1000:
            self._evaluation_cache.clear()
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        # Sắp xếp nước đi trước khi đánh giá
        ordered_moves = self.order_moves(board, legal_moves)
        
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in ordered_moves:
            board.push(move)
            
            if board.turn == chess.BLACK:
                move_value = self.minimax(board, self.depth - 1, alpha, beta, False)
            else:
                move_value = self.minimax(board, self.depth - 1, alpha, beta, True)
            
            board.pop()
            
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
