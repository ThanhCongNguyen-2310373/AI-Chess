"""
Giao diện game sử dụng Pygame
"""
import pygame
import chess
import chess.svg
from config import *


class ChessUI:
    """Lớp quản lý giao diện pygame"""
    
    def __init__(self):
        pygame.init()
        
        # Tăng chiều cao để chứa info bar ở trênagent
        self.info_bar_height = 60
        total_height = SCREEN_HEIGHT + self.info_bar_height
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, total_height))
        pygame.display.set_caption("AI Chess - BTL2")
        self.clock = pygame.time.Clock()
        
        # Load hình ảnh quân cờ
        self.piece_images = self._load_piece_images()
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.info_font = pygame.font.Font(None, 28)
        
        # Trạng thái UI
        self.selected_square = None
        self.valid_moves = []
        self.move_history = []  # Lịch sử nước đi của người chơi (để undo)
        self.is_paused = False  # Trạng thái pause
    
    def _load_piece_images(self):
        """
        Load hình ảnh quân cờ từ folder assets
        """
        images = {}
        
        # Mapping piece symbols to image files
        piece_files = {
            'P': 'assets/Team_White/pawn_white.png',
            'N': 'assets/Team_White/knight_white.png',
            'B': 'assets/Team_White/bishop_white.png',
            'R': 'assets/Team_White/rook_white.png',
            'Q': 'assets/Team_White/queen_white.png',
            'K': 'assets/Team_White/king_white.png',
            'p': 'assets/Team_Black/pawn_black.png',
            'n': 'assets/Team_Black/knight_black.png',
            'b': 'assets/Team_Black/bishop_black.png',
            'r': 'assets/Team_Black/rook_black.png',
            'q': 'assets/Team_Black/queen_black.png',
            'k': 'assets/Team_Black/king_black.png',
        }
        
        # Load và scale images
        for piece_char, file_path in piece_files.items():
            try:
                img = pygame.image.load(file_path)
                # Scale to fit square size (with some padding)
                img = pygame.transform.scale(img, (int(SQUARE_SIZE * 0.8), int(SQUARE_SIZE * 0.8)))
                images[piece_char] = img
            except Exception as e:
                print(f"Lỗi load image {file_path}: {e}")
                # Fallback: tạo surface trống
                images[piece_char] = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        
        return images
    
    def draw_board(self, board, last_move=None):
        """
        Vẽ bàn cờ
        
        Args:
            board: chess.Board
            last_move: Nước đi vừa rồi để highlight
        """
        # Vẽ các ô cờ
        for row in range(8):
            for col in range(8):
                # Xác định màu ô
                color = COLOR_WHITE if (row + col) % 2 == 0 else COLOR_BLACK
                
                # Tính vị trí (shift xuống để dành chỗ cho info bar)
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE + self.info_bar_height
                
                # Vẽ ô
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # Highlight ô được chọn
                square_idx = (7 - row) * 8 + col
                if self.selected_square == square_idx:
                    pygame.draw.rect(self.screen, COLOR_SELECTED, 
                                   (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # Highlight nước đi cuối
                if last_move:
                    if square_idx == last_move.from_square or square_idx == last_move.to_square:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                        s.set_alpha(128)
                        s.fill(COLOR_HIGHLIGHT)
                        self.screen.blit(s, (x, y))
                
                # Vẽ quân cờ
                piece = board.piece_at(square_idx)
                if piece:
                    piece_char = piece.symbol()
                    if piece_char in self.piece_images:
                        img = self.piece_images[piece_char]
                        # Căn giữa hình ảnh trong ô
                        img_x = x + (SQUARE_SIZE - img.get_width()) // 2
                        img_y = y + (SQUARE_SIZE - img.get_height()) // 2
                        self.screen.blit(img, (img_x, img_y))
        
        # Vẽ các nước đi hợp lệ
        for move in self.valid_moves:
            to_square = move.to_square
            col = to_square % 8
            row = 7 - (to_square // 8)
            x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            y = row * SQUARE_SIZE + SQUARE_SIZE // 2 + self.info_bar_height
            pygame.draw.circle(self.screen, (0, 255, 0), (x, y), 10)
    
    def draw_info_bar(self, text, color=(255, 255, 255)):
        """
        Vẽ thanh thông tin ở trên cùng (trên bàn cờ)
        
        Args:
            text: Text cần hiển thị
            color: Màu chữ
        """
        # Vẽ background cho info bar
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, SCREEN_WIDTH, self.info_bar_height))
        pygame.draw.line(self.screen, (100, 100, 100), 
                        (0, self.info_bar_height), 
                        (SCREEN_WIDTH, self.info_bar_height), 2)
        
        # Vẽ text CANH LỀ TRÁI (không đè hint controls)
        text_surface = self.info_font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.left = 15  # Canh lề trái
        text_rect.centery = self.info_bar_height // 2
        self.screen.blit(text_surface, text_rect)
        
        # Vẽ hint controls ở góc phải
        hint_text = "U: Undo | R: Pause | ESC: Quit"
        hint_surface = self.small_font.render(hint_text, True, (180, 180, 180))
        hint_rect = hint_surface.get_rect()
        hint_rect.right = SCREEN_WIDTH - 10
        hint_rect.centery = self.info_bar_height // 2
        self.screen.blit(hint_surface, hint_rect)
    
    def draw_info(self, text, y_offset=10, color=(255, 255, 255)):
        """
        Vẽ thông tin lên màn hình (deprecated - dùng draw_info_bar thay thế)
        
        Args:
            text: Text cần hiển thị
            y_offset: Vị trí y
            color: Màu chữ (mặc định trắng)
        """
        text_surface = self.small_font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, y_offset + self.info_bar_height)
        
        # Vẽ background
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)
        
        self.screen.blit(text_surface, text_rect)
    
    def draw_pause_menu(self):
        """Vẽ menu pause"""
        # Vẽ overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT + self.info_bar_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font.render("PAUSED", True, (255, 255, 0))
        title_rect = title.get_rect()
        title_rect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT + self.info_bar_height) // 2 - 50)
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "Press R to Resume",
            "Press U to Undo Move",
            "Press ESC to Quit"
        ]
        
        for i, text in enumerate(instructions):
            text_surface = self.small_font.render(text, True, (200, 200, 200))
            text_rect = text_surface.get_rect()
            text_rect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT + self.info_bar_height) // 2 + i * 30)
            self.screen.blit(text_surface, text_rect)
    
    def draw_game_over(self, result_text):
        """
        Vẽ màn hình kết thúc
        
        Args:
            result_text: Kết quả trận đấu (English)
        """
        # Vẽ overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT + self.info_bar_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ text
        text_surface = self.font.render(result_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT + self.info_bar_height) // 2)
        self.screen.blit(text_surface, text_rect)
        
        # Hướng dẫn
        help_text = self.small_font.render("Press SPACE to restart, ESC to quit", 
                                          True, (200, 200, 200))
        help_rect = help_text.get_rect()
        help_rect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT + self.info_bar_height) // 2 + 50)
        self.screen.blit(help_text, help_rect)
    
    def get_square_from_mouse(self, pos):
        """
        Chuyển vị trí chuột thành square index
        
        Args:
            pos: (x, y) của chuột
        
        Returns:
            Square index (0-63) hoặc None
        """
        x, y = pos
        # Trừ đi info_bar_height
        y -= self.info_bar_height
        
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        
        if 0 <= col < 8 and 0 <= row < 8:
            return (7 - row) * 8 + col
        
        return None
    
    def handle_click(self, board, pos):
        """
        Xử lý click chuột
        
        Args:
            board: chess.Board
            pos: Vị trí click
        
        Returns:
            chess.Move nếu có nước đi hợp lệ, None nếu không
        """
        square = self.get_square_from_mouse(pos)
        
        if square is None:
            return None
        
        # Nếu chưa chọn ô nào
        if self.selected_square is None:
            piece = board.piece_at(square)
            if piece and piece.color == board.turn:
                self.selected_square = square
                # Tìm các nước đi hợp lệ từ ô này
                self.valid_moves = [m for m in board.legal_moves 
                                   if m.from_square == square]
        else:
            # Đã chọn ô, kiểm tra xem có di chuyển được không
            move = chess.Move(self.selected_square, square)
            
            # Kiểm tra promotion
            piece = board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN:
                # Nếu tốt đến hàng cuối, phong hậu
                if (piece.color == chess.WHITE and square >= 56) or \
                   (piece.color == chess.BLACK and square <= 7):
                    move = chess.Move(self.selected_square, square, 
                                    promotion=chess.QUEEN)
            
            self.selected_square = None
            self.valid_moves = []
            
            if move in board.legal_moves:
                return move
        
        return None
    
    def save_move_for_undo(self, board_fen, move):
        """
        Lưu nước đi để có thể undo
        
        Args:
            board_fen: FEN của board trước khi đi
            move: Nước đi
        """
        self.move_history.append((board_fen, move))
    
    def can_undo(self):
        """Kiểm tra có thể undo không"""
        return len(self.move_history) >= 1  # Cần ít nhất 1 nước của người chơi
    
    def get_undo_state(self):
        """
        Lấy trạng thái board để undo (CHỈ undo nước của người chơi vừa đi)
        
        Returns:
            FEN của board sau khi undo, hoặc None
        """
        if not self.can_undo():
            return None
        
        # Bỏ 1 nước cuối (nước của người chơi vừa đi)
        self.move_history.pop()
        
        if self.move_history:
            return self.move_history[-1][0]  # FEN sau nước cuối còn lại
        else:
            return chess.Board().fen()  # Board ban đầu
    
    def clear_history(self):
        """Xóa lịch sử (khi restart)"""
        self.move_history.clear()
    
    def toggle_pause(self):
        """Bật/tắt pause"""
        self.is_paused = not self.is_paused
    
    def update(self):
        """Cập nhật màn hình"""
        pygame.display.flip()
        self.clock.tick(FPS)
    
    def quit(self):
        """Thoát pygame"""
        pygame.quit()
