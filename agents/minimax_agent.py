"""
Agent sử dụng thuật toán Minimax với Alpha-Beta Pruning
"""
import chess
from .base_agent import BaseAgent
from utils import get_piece_value, get_position_value, is_endgame
from config import MINIMAX_DEPTH


class MinimaxAgent(BaseAgent):
    """Agent sử dụng Minimax với Alpha-Beta Pruning (Nâng cấp PRO)"""
    
    def __init__(self, depth=MINIMAX_DEPTH):
        super().__init__(name="Minimax Agent")
        self.depth = depth
        self.transposition_table = {}  # Bảng băm vị trí (Transposition Table)
        self.quiescence_depth_limit = 10  # Giới hạn độ sâu quiescence search
    
    def order_moves(self, board, moves, best_move_hint=None):
        """
        Sắp xếp nước đi để tối ưu Alpha-Beta Pruning
        Nước đi tốt hơn được xét trước -> pruning nhiều hơn
        
        Args:
            board: Bàn cờ hiện tại
            moves: Danh sách nước đi cần sắp xếp
            best_move_hint: Nước đi tốt nhất từ iteration trước (Iterative Deepening)
        
        Returns:
            Danh sách nước đi đã sắp xếp
        """
        move_scores = []
        
        for move in moves:
            score = 0
            
            # 0. HIGHEST PRIORITY: Best move từ iteration trước
            if best_move_hint and move == best_move_hint:
                score += 100000  # Ưu tiên cực cao!
            
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
        
        # 2. Mobility (Khả năng di chuyển) - ĐÃ CẢI TIẾN ĐỂ TRÁNH STALEMATE
        white_mobility = 0
        black_mobility = 0
        
        try:
            # Tính mobility cho bên ĐANG CÓ LƯỢT ĐI
            if board.turn == chess.WHITE:
                white_mobility = len(list(board.legal_moves))
            else:
                black_mobility = len(list(board.legal_moves))
            
            # Đảo lượt để tính cho bên kia (null move)
            board.push(chess.Move.null())
            if board.turn == chess.WHITE:
                white_mobility = len(list(board.legal_moves))
            else:
                black_mobility = len(list(board.legal_moves))
            board.pop()
            
        except Exception:
            # Xử lý trường hợp không thể đi null move (ví dụ: đang bị chiếu)
            # Nếu đang bị chiếu, legal_moves đã được tính ở trên
            if board.turn == chess.WHITE:
                black_mobility = 0  # Giả sử bên kia không thể đi
            else:
                white_mobility = 0
        
        # *** LOGIC TRÁNH STALEMATE ***
        winning_margin = 400  # Thắng hơn 1 Xe hoặc 1 Mã+Tốt
        is_white_winning = white_material > black_material + winning_margin
        is_black_winning = black_material > white_material + winning_margin
        
        if is_white_winning:
            # Trắng đang thắng lớn
            score += white_mobility * 10  # 1. Luôn thưởng cho mobility của mình
            
            # 2. Xử lý mobility của Đen (để tránh stalemate)
            if black_mobility < 5:
                # Phạt nặng nếu dồn Đen vào thế quá ít nước đi
                # Càng ít nước, phạt càng nặng (0 nước = -125 điểm)
                penalty = (5 - black_mobility) * 25
                score -= penalty
            else:
                # Thưởng nhẹ vì giữ cho Đen "còn thở" để mate
                score += black_mobility * 5
        
        elif is_black_winning:
            # Đen đang thắng lớn
            score -= black_mobility * 10  # 1. Luôn thưởng cho mobility của mình (Đen)
            
            # 2. Xử lý mobility của Trắng
            if white_mobility < 5:
                # Phạt nặng nếu dồn Trắng vào thế quá ít nước đi
                penalty = (5 - white_mobility) * 25
                score += penalty  # Phạt (cộng điểm cho Đen)
            else:
                # Thưởng nhẹ
                score -= white_mobility * 5  # Thưởng (trừ điểm của Trắng)
        
        else:
            # 3. Nếu ván cờ cân bằng, dùng logic cũ
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
        
        # 8. Passed Pawns (Tốt thông) - tốt không bị chặn bởi tốt địch
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                
                is_passed = True
                if piece.color == chess.WHITE:
                    # Kiểm tra các hàng phía trước
                    for check_rank in range(rank + 1, 8):
                        # Kiểm tra cùng cột và 2 cột bên cạnh
                        for check_file in [file - 1, file, file + 1]:
                            if 0 <= check_file < 8:
                                check_sq = chess.square(check_file, check_rank)
                                check_piece = board.piece_at(check_sq)
                                if check_piece and check_piece.piece_type == chess.PAWN and check_piece.color == chess.BLACK:
                                    is_passed = False
                                    break
                        if not is_passed:
                            break
                    
                    if is_passed:
                        # Thưởng tùy theo vị trí: tốt càng gần promotion càng giá trị
                        bonus = 10 * (rank - 1)  # Rank 2 = 10, Rank 7 = 60
                        score += bonus
                
                else:  # BLACK pawn
                    for check_rank in range(0, rank):
                        for check_file in [file - 1, file, file + 1]:
                            if 0 <= check_file < 8:
                                check_sq = chess.square(check_file, check_rank)
                                check_piece = board.piece_at(check_sq)
                                if check_piece and check_piece.piece_type == chess.PAWN and check_piece.color == chess.WHITE:
                                    is_passed = False
                                    break
                        if not is_passed:
                            break
                    
                    if is_passed:
                        bonus = 10 * (6 - rank)  # Rank 6 = 10, Rank 1 = 60
                        score -= bonus
        
        # 9. Rook on Open/Semi-Open Files (Xe trên cột mở/nửa mở)
        for file in range(8):
            white_pawns = 0
            black_pawns = 0
            white_rook = False
            black_rook = False
            
            for rank in range(8):
                sq = chess.square(file, rank)
                piece = board.piece_at(sq)
                if piece:
                    if piece.piece_type == chess.PAWN:
                        if piece.color == chess.WHITE:
                            white_pawns += 1
                        else:
                            black_pawns += 1
                    elif piece.piece_type == chess.ROOK:
                        if piece.color == chess.WHITE:
                            white_rook = True
                        else:
                            black_rook = True
            
            # Open file (không có tốt nào)
            if white_pawns == 0 and black_pawns == 0:
                if white_rook:
                    score += 20
                if black_rook:
                    score -= 20
            # Semi-open file (chỉ có tốt địch)
            elif white_pawns == 0 and black_pawns > 0:
                if white_rook:
                    score += 15
            elif black_pawns == 0 and white_pawns > 0:
                if black_rook:
                    score -= 15
        
        # 10. Bishop Pair (Cặp tượng) - rất mạnh trong endgame
        white_bishops = len(list(board.pieces(chess.BISHOP, chess.WHITE)))
        black_bishops = len(list(board.pieces(chess.BISHOP, chess.BLACK)))
        
        if white_bishops >= 2:
            score += 30 if endgame else 20  # Mạnh hơn trong endgame
        if black_bishops >= 2:
            score -= 30 if endgame else 20
        
        # 11. ENDGAME: Dồn Vua địch vào góc khi thắng thế
        if endgame:
            winning_side = None
            losing_king_sq = None
            winning_king_sq = None
            
            # Xác định bên nào đang thắng (chênh lệch >= 300 = 1 Mã/Tượng)
            if white_material > black_material + 300:
                winning_side = chess.WHITE
                losing_king_sq = board.king(chess.BLACK)
                winning_king_sq = board.king(chess.WHITE)
            elif black_material > white_material + 300:
                winning_side = chess.BLACK
                losing_king_sq = board.king(chess.WHITE)
                winning_king_sq = board.king(chess.BLACK)
            
            if winning_side and losing_king_sq is not None and winning_king_sq is not None:
                # A. Thưởng khi đẩy Vua địch ra xa trung tâm (vào góc)
                enemy_king_file = chess.square_file(losing_king_sq)
                enemy_king_rank = chess.square_rank(losing_king_sq)
                
                # Khoảng cách Manhattan đến tâm bàn cờ (3.5, 3.5)
                dist_to_center = abs(enemy_king_file - 3.5) + abs(enemy_king_rank - 3.5)
                
                # Càng xa tâm càng tốt (max = 7 khi ở góc)
                corral_bonus = dist_to_center * 15
                
                # B. Thưởng khi Vua mình áp sát Vua địch (King Opposition)
                friendly_king_file = chess.square_file(winning_king_sq)
                friendly_king_rank = chess.square_rank(winning_king_sq)
                
                # Khoảng cách Manhattan giữa 2 Vua
                king_dist = abs(friendly_king_file - enemy_king_file) + \
                           abs(friendly_king_rank - enemy_king_rank)
                
                # Càng gần càng tốt (min = 1, max = 14)
                opposition_bonus = (14 - king_dist) * 10
                
                # Cộng/trừ điểm tùy bên nào thắng
                if winning_side == chess.WHITE:
                    score += corral_bonus + opposition_bonus
                else:
                    score -= (corral_bonus + opposition_bonus)
        
        return score
    
    def quiescence_search(self, board, alpha, beta, maximizing_player, depth=0):
        """
        Quiescence Search - Tìm kiếm "tĩnh" để tránh Horizon Effect
        Chỉ tìm kiếm các nước đi "ồn ào" (captures, promotions)
        
        Args:
            board: Bàn cờ hiện tại
            alpha: Alpha value
            beta: Beta value
            maximizing_player: True nếu đang tối đa hóa
            depth: Độ sâu quiescence (để giới hạn)
        
        Returns:
            Điểm đánh giá sau khi bàn cờ "tĩnh"
        """
        self.nodes_searched += 1
        
        # Kiểm tra game over
        if board.is_game_over():
            return self.evaluate_board(board)
        
        # Giới hạn độ sâu quiescence
        if depth >= self.quiescence_depth_limit:
            return self.evaluate_board(board)
        
        # Đánh giá tĩnh (stand pat)
        stand_pat = self.evaluate_board(board)
        
        # Chỉ xét các nước "ồn ào" (captures và promotions)
        violent_moves = []
        for move in board.legal_moves:
            if board.is_capture(move) or move.promotion:
                violent_moves.append(move)
        
        # Nếu không có nước ồn ào, trả về đánh giá tĩnh
        if not violent_moves:
            return stand_pat
        
        # Sắp xếp các nước ồn ào (MVV-LVA)
        ordered_moves = self.order_moves(board, violent_moves)
        
        # Tìm kiếm giống minimax (max/min style)
        if maximizing_player:
            # Stand pat (có thể không đi nước ồn ào nào)
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
            
            max_eval = stand_pat
            for move in ordered_moves:
                board.push(move)
                eval_score = self.quiescence_search(board, alpha, beta, False, depth + 1)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            # Stand pat
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat
            
            min_eval = stand_pat
            for move in ordered_moves:
                board.push(move)
                eval_score = self.quiescence_search(board, alpha, beta, True, depth + 1)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Thuật toán Minimax với Alpha-Beta Pruning + Transposition Table + Quiescence
        (ĐÃ CẢI TIẾN: Tránh lặp lại 3 lần)
        
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
        
        # Kiểm tra game over trước
        if board.is_game_over():
            return self.evaluate_board(board)
        
        # Transposition Table lookup
        fen_key = board.fen()
        if fen_key in self.transposition_table:
            stored_depth, stored_score = self.transposition_table[fen_key]
            if stored_depth >= depth:
                return stored_score
        
        # Điều kiện dừng - GỌI QUIESCENCE SEARCH thay vì evaluate_board
        if depth == 0:
            score = self.quiescence_search(board, alpha, beta, maximizing_player)
            self.transposition_table[fen_key] = (0, score)
            return score
        
        # Lấy và sắp xếp nước đi (Move Ordering để tăng pruning)
        legal_moves = list(board.legal_moves)
        ordered_moves = self.order_moves(board, legal_moves)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in ordered_moves:
                board.push(move)
                
                # ### CẢI TIẾN: KIỂM TRA LẶP LẠI ###
                # Nếu nước đi này tạo ra 1 thế cờ đã lặp lại (lần 2),
                # coi như hòa cờ (0 điểm) để agent tránh/chọn nó.
                if board.is_repetition(2):
                    eval_score = 0
                else:
                    eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                
                board.pop()
                
                # MATE SCORE OPTIMIZATION: Ưu tiên mate ngắn nhất
                # Nếu tìm thấy đường thắng, trừ 1 để ưu tiên đường ngắn hơn
                if eval_score > 999000:  # Điểm mate thắng
                    eval_score -= 1
                # Nếu bị thua, cộng 1 để ưu tiên thua "lâu nhất"
                elif eval_score < -999000:  # Điểm mate thua
                    eval_score += 1
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            # Lưu vào Transposition Table
            self.transposition_table[fen_key] = (depth, max_eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                board.push(move)
                
                # ### CẢI TIẾN: KIỂM TRA LẶP LẠI ###
                if board.is_repetition(2):
                    eval_score = 0
                else:
                    eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                
                board.pop()
                
                # MATE SCORE OPTIMIZATION: Ưu tiên mate ngắn nhất
                if eval_score > 999000:  # Điểm mate thắng
                    eval_score -= 1
                elif eval_score < -999000:  # Điểm mate thua
                    eval_score += 1
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            # Lưu vào Transposition Table
            self.transposition_table[fen_key] = (depth, min_eval)
            return min_eval
    
    def get_move(self, board):
        """
        Tìm nước đi tốt nhất với Iterative Deepening
        
        Args:
            board: Bàn cờ hiện tại
        
        Returns:
            Nước đi tốt nhất
        """
        self.reset_stats()
        self.transposition_table.clear()  # Clear cache mỗi lần chọn nước
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = None
        
        # ITERATIVE DEEPENING: Tìm kiếm từ depth=1 đến depth=target
        for current_depth in range(1, self.depth + 1):
            # Sắp xếp nước đi - ƯU TIÊN best_move từ iteration trước
            ordered_moves = self.order_moves(board, legal_moves, best_move)
            
            best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
            alpha = float('-inf')
            beta = float('inf')
            temp_best_move = None
            
            # Duyệt qua các nước đi đã sắp xếp
            for move in ordered_moves:
                board.push(move)
                
                # Gọi minimax với current_depth (không phải self.depth)
                if board.turn == chess.BLACK:  # Sau khi đi, đến lượt đen
                    # Trắng vừa đi, tìm max
                    move_value = self.minimax(board, current_depth - 1, alpha, beta, False)
                else:  # Sau khi đi, đến lượt trắng
                    # Đen vừa đi, tìm min
                    move_value = self.minimax(board, current_depth - 1, alpha, beta, True)
                
                board.pop()
                
                # Cập nhật nước đi tốt nhất cho iteration này
                if board.turn == chess.WHITE:
                    if move_value > best_value:
                        best_value = move_value
                        temp_best_move = move
                        alpha = max(alpha, move_value)
                else:
                    if move_value < best_value:
                        best_value = move_value
                        temp_best_move = move
                        beta = min(beta, move_value)
            
            # Sau mỗi iteration, cập nhật best_move nếu tìm được
            if temp_best_move:
                best_move = temp_best_move
        
        return best_move
