"""
Các hàm tiện ích cho dự án
"""
import chess
import numpy as np
from config import *


def get_piece_value(piece):
    """Lấy giá trị của quân cờ"""
    if piece is None:
        return 0
    return PIECE_VALUES.get(piece.symbol().upper(), 0)


def get_position_value(piece, square, is_endgame=False):
    """
    Lấy giá trị vị trí của quân cờ dựa trên Piece-Square Tables
    
    Args:
        piece: Quân cờ (chess.Piece)
        square: Vị trí (0-63)
        is_endgame: Có phải ván cuối không
    
    Returns:
        Điểm thưởng vị trí
    """
    if piece is None:
        return 0
    
    piece_type = piece.symbol().upper()
    
    # Đảo ngược bảng nếu là quân đen
    if piece.color == chess.BLACK:
        square = 63 - square
    
    if piece_type == 'P':
        return PAWN_TABLE[square]
    elif piece_type == 'N':
        return KNIGHT_TABLE[square]
    elif piece_type == 'B':
        return BISHOP_TABLE[square]
    elif piece_type == 'R':
        return ROOK_TABLE[square]
    elif piece_type == 'Q':
        return QUEEN_TABLE[square]
    elif piece_type == 'K':
        if is_endgame:
            return KING_END_GAME_TABLE[square]
        else:
            return KING_MIDDLE_GAME_TABLE[square]
    
    return 0


def is_endgame(board):
    """
    Kiểm tra xem có phải giai đoạn cuối ván không
    (Khi không còn Hậu hoặc tổng giá trị quân < 1300)
    """
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + \
             len(board.pieces(chess.QUEEN, chess.BLACK))
    
    if queens == 0:
        return True
    
    # Tính tổng giá trị quân cờ
    total_material = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            total_material += get_piece_value(piece)
    
    return total_material < 1300


def fen_to_tensor(fen):
    """
    Chuyển FEN string thành tensor 3D (8x8x12)
    12 channels: 6 loại quân x 2 màu
    
    Args:
        fen: FEN string
    
    Returns:
        numpy array shape (8, 8, 12)
    """
    board = chess.Board(fen)
    tensor = np.zeros((8, 8, 12), dtype=np.float32)
    
    # Mapping: piece_type -> channel index
    piece_to_channel = {
        chess.PAWN: 0,
        chess.KNIGHT: 1,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4,
        chess.KING: 5
    }
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)  # Đảo ngược vì chess.SQUARES đi từ dưới lên
            col = square % 8
            channel = piece_to_channel[piece.piece_type]
            
            # Thêm 6 nếu là quân đen
            if piece.color == chess.BLACK:
                channel += 6
            
            tensor[row, col, channel] = 1.0
    
    return tensor


def count_material(board):
    """
    Đếm tổng giá trị quân cờ cho cả hai bên
    
    Returns:
        (white_material, black_material)
    """
    white_material = 0
    black_material = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = get_piece_value(piece)
            if piece.color == chess.WHITE:
                white_material += value
            else:
                black_material += value
    
    return white_material, black_material


def format_move(move):
    """Format nước đi để hiển thị đẹp"""
    return move.uci()


def print_board(board):
    """In bàn cờ ra console (để debug)"""
    print("\n" + str(board) + "\n")
