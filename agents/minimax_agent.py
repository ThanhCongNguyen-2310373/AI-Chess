"""
Agent sử dụng thuật toán Minimax với Alpha-Beta Pruning
"""
import chess
from .base_agent import BaseAgent
from utils import get_piece_value, get_position_value, is_endgame
from config import MINIMAX_DEPTH


class MinimaxAgent(BaseAgent):
    """Agent sử dụng Minimax với Alpha-Beta Pruning (Nâng cấp)"""
    
    def __init__(self, depth=MINIMAX_DEPTH):
        super().__init__(name="Minimax Agent")
        self.depth = depth
    
    def order_moves(self, board, moves):
        """
        Sắp xếp nước đi để tối ưu Alpha-Beta Pruning
        Nước đi tốt hơn được xét trước -> pruning nhiều hơn
        
        Args:
            board: Bàn cờ hiện tại
            moves: Danh sách nước đi cần sắp xếp
        
        Returns:
            Danh sách nước đi đã sắp xếp
        """
        move_scores = []
        
        for move in moves:
            score = 0
            
            # 1. Ưu tiên bắt quân (captures)
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                moving_piece = board.piece_at(move.from_square)
                if captured_piece and moving_piece:
                    # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
                    score += 1000 + get_piece_value(captured_piece) - get_piece_value(moving_piece) // 10
            
            # 2. Ưu tiên phong cấp (promotions)
            if move.promotion:
                score += 900
            
            # 3. Ưu tiên chiếu hết (checks)
            board.push(move)
            if board.is_checkmate():
                score += 10000  # Chiếu hết là tốt nhất!
            elif board.is_check():
                score += 100
            board.pop()
            
            # 4. Ưu tiên nước đi vào trung tâm
            to_file = chess.square_file(move.to_square)
            to_rank = chess.square_rank(move.to_square)
            if (to_file in [3, 4] and to_rank in [3, 4]):  # e4, e5, d4, d5
                score += 30
            
            move_scores.append((score, move))
        
        # Sắp xếp giảm dần theo score
        move_scores.sort(reverse=True, key=lambda x: x[0])
        
        return [move for _, move in move_scores]
    
    def evaluate_board(self, board):
        """
        Hàm đánh giá bàn cờ (nâng cấp với nhiều yếu tố hơn)
        
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
        
        # 1. Đánh giá từng quân cờ (Material + Position)
        white_material = 0
        black_material = 0
        
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
                    white_material += piece_value
                else:
                    score -= total_value
                    black_material += piece_value
        
        # 2. Mobility (Khả năng di chuyển) - càng nhiều nước đi càng tốt
        white_mobility = len(list(board.legal_moves)) if board.turn == chess.WHITE else 0
        black_mobility = len(list(board.legal_moves)) if board.turn == chess.BLACK else 0
        
        # Simulate để đếm mobility của bên kia
        board.push(chess.Move.null())  # Null move
        if board.turn == chess.BLACK:
            white_mobility = len(list(board.legal_moves))
        else:
            black_mobility = len(list(board.legal_moves))
        board.pop()
        
        score += (white_mobility - black_mobility) * 10
        
        # 3. King Safety (An toàn vua) - quan trọng trong opening/middlegame
        if not endgame:
            white_king_sq = board.king(chess.WHITE)
            black_king_sq = board.king(chess.BLACK)
            
            # Kiểm tra vua có được bảo vệ bởi tốt không
            if white_king_sq:
                # Đếm tốt trắng quanh vua trắng
                king_file = chess.square_file(white_king_sq)
                king_rank = chess.square_rank(white_king_sq)
                pawn_shield = 0
                for file_offset in [-1, 0, 1]:
                    f = king_file + file_offset
                    if 0 <= f < 8 and king_rank < 7:
                        sq = chess.square(f, king_rank + 1)
                        piece = board.piece_at(sq)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                            pawn_shield += 15
                score += pawn_shield
            
            if black_king_sq:
                king_file = chess.square_file(black_king_sq)
                king_rank = chess.square_rank(black_king_sq)
                pawn_shield = 0
                for file_offset in [-1, 0, 1]:
                    f = king_file + file_offset
                    if 0 <= f < 8 and king_rank > 0:
                        sq = chess.square(f, king_rank - 1)
                        piece = board.piece_at(sq)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                            pawn_shield += 15
                score -= pawn_shield
        
        # 4. Pawn Structure (Cấu trúc tốt)
        # Tốt đơn (isolated pawn) bị phạt
        # Tốt kép (doubled pawn) bị phạt
        for file in range(8):
            white_pawns_on_file = 0
            black_pawns_on_file = 0
            
            for rank in range(8):
                sq = chess.square(file, rank)
                piece = board.piece_at(sq)
                if piece and piece.piece_type == chess.PAWN:
                    if piece.color == chess.WHITE:
                        white_pawns_on_file += 1
                    else:
                        black_pawns_on_file += 1
            
            # Phạt tốt kép
            if white_pawns_on_file > 1:
                score -= 10 * (white_pawns_on_file - 1)
            if black_pawns_on_file > 1:
                score += 10 * (black_pawns_on_file - 1)
        
        # 5. Control Center (Kiểm soát trung tâm) - quan trọng!
        center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        for sq in center_squares:
            # Kiểm tra quân nào đang chiếm trung tâm
            piece = board.piece_at(sq)
            if piece:
                if piece.color == chess.WHITE:
                    score += 20
                else:
                    score -= 20
            
            # Kiểm tra quân nào đang tấn công trung tâm
            white_attackers = len(board.attackers(chess.WHITE, sq))
            black_attackers = len(board.attackers(chess.BLACK, sq))
            score += (white_attackers - black_attackers) * 5
        
        # 6. Check penalty/bonus
        if board.is_check():
            if board.turn == chess.WHITE:
                score -= 50  # Trắng bị chiếu
            else:
                score += 50  # Đen bị chiếu
        
        # 7. Development bonus (Opening phase)
        if not endgame and board.fullmove_number <= 15:
            # Thưởng cho việc phát triển quân
            white_developed = 0
            black_developed = 0
            
            # Kiểm tra mã và tượng có rời khỏi hàng đầu chưa
            for piece_type in [chess.KNIGHT, chess.BISHOP]:
                for square in board.pieces(piece_type, chess.WHITE):
                    if chess.square_rank(square) > 0:  # Đã rời hàng 1
                        white_developed += 10
                for square in board.pieces(piece_type, chess.BLACK):
                    if chess.square_rank(square) < 7:  # Đã rời hàng 8
                        black_developed += 10
            
            score += white_developed - black_developed
        
        return score
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Thuật toán Minimax với Alpha-Beta Pruning (có Move Ordering)
        
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
        
        # Lấy và sắp xếp nước đi (Move Ordering để tăng pruning)
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
                    break  # Beta cutoff
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
                    break  # Alpha cutoff
            return min_eval
    
    def get_move(self, board):
        """
        Tìm nước đi tốt nhất bằng Minimax (với Move Ordering)
        
        Args:
            board: Bàn cờ hiện tại
        
        Returns:
            Nước đi tốt nhất
        """
        self.reset_stats()
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        # Sắp xếp nước đi để xét nước tốt trước
        ordered_moves = self.order_moves(board, legal_moves)
        
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Duyệt qua các nước đi đã sắp xếp
        for move in ordered_moves:
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
