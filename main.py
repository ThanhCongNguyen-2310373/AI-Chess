"""
File chính để chạy game AI Chess
"""
import pygame
import chess
import sys
from game_ui import ChessUI
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.ml_agent import MLAgent


class ChessGame:
    """Lớp quản lý game"""
    
    def __init__(self, white_agent=None, black_agent=None, human_player=None):
        """
        Khởi tạo game
        
        Args:
            white_agent: Agent chơi quân trắng (None = người chơi)
            black_agent: Agent chơi quân đen (None = người chơi)
            human_player: 'white', 'black', hoặc None (AI vs AI)
        """
        self.board = chess.Board()
        self.ui = ChessUI()
        self.white_agent = white_agent
        self.black_agent = black_agent
        self.human_player = human_player
        self.last_move = None
        self.game_over = False
        self.result_text = ""
        
    def get_current_agent(self):
        """Lấy agent hiện tại"""
        if self.board.turn == chess.WHITE:
            return self.white_agent
        else:
            return self.black_agent
    
    def is_human_turn(self):
        """Kiểm tra có phải lượt người chơi không"""
        if self.human_player == 'white' and self.board.turn == chess.WHITE:
            return True
        if self.human_player == 'black' and self.board.turn == chess.BLACK:
            return True
        return False
    
    def make_ai_move(self):
        """Agent thực hiện nước đi"""
        agent = self.get_current_agent()
        if agent:
            # Hiển thị "đang suy nghĩ..." trước khi tính toán
            self.ui.draw_board(self.board, self.last_move)
            turn_text = "Trắng" if self.board.turn == chess.WHITE else "Đen"
            self.ui.draw_info(f"Lượt: {turn_text}", 10)
            self.ui.draw_info(f"{agent.name} đang suy nghĩ...", 40, color=(255, 150, 0))
            self.ui.update()
            
            print(f"\n{agent.name} đang suy nghĩ...")
            move = agent.get_move(self.board)
            if move:
                self.board.push(move)
                self.last_move = move
                print(f"  → Di chuyển: {move.uci()}")
                stats = agent.get_stats()
                print(f"  → Nodes searched: {stats['nodes_searched']}")
    
    def check_game_over(self):
        """Kiểm tra game kết thúc"""
        if self.board.is_checkmate():
            winner = "Đen" if self.board.turn == chess.WHITE else "Trắng"
            self.result_text = f"{winner} thắng (Chiếu bí)!"
            self.game_over = True
        elif self.board.is_stalemate():
            self.result_text = "Hòa (Stalemate)!"
            self.game_over = True
        elif self.board.is_insufficient_material():
            self.result_text = "Hòa (Không đủ quân)!"
            self.game_over = True
        elif self.board.is_fifty_moves():
            self.result_text = "Hòa (50 nước)!"
            self.game_over = True
        elif self.board.is_repetition():
            self.result_text = "Hòa (Lặp lại)!"
            self.game_over = True
    
    def reset(self):
        """Reset game"""
        self.board.reset()
        self.last_move = None
        self.game_over = False
        self.result_text = ""
    
    def run(self):
        """Vòng lặp chính của game"""
        running = True
        
        while running:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset()
                
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if self.is_human_turn():
                        move = self.ui.handle_click(self.board, event.pos)
                        if move:
                            self.board.push(move)
                            self.last_move = move
                            
                            # VẼ NGAY SAU KHI NGƯỜI CHƠI ĐI
                            self.ui.draw_board(self.board, self.last_move)
                            turn_text = "Trắng" if self.board.turn == chess.WHITE else "Đen"
                            self.ui.draw_info(f"Lượt: {turn_text}", 10)
                            self.ui.update()
                            
                            # Kiểm tra game over sau nước của người
                            self.check_game_over()
            
            # AI di chuyển (nếu không phải lượt người)
            if not self.game_over and not self.is_human_turn():
                self.make_ai_move()
            
            # Kiểm tra kết thúc
            self.check_game_over()
            
            # Vẽ giao diện
            self.ui.draw_board(self.board, self.last_move)
            
            # Hiển thị thông tin
            turn_text = "Trắng" if self.board.turn == chess.WHITE else "Đen"
            self.ui.draw_info(f"Lượt: {turn_text}", 10)
            
            if self.game_over:
                self.ui.draw_game_over(self.result_text)
            
            self.ui.update()
        
        self.ui.quit()


def main():
    """Hàm main"""
    print("=" * 60)
    print("AI CHESS - BÀI TẬP LỚN 2")
    print("=" * 60)
    print("\nChọn chế độ chơi:")
    print("1. Người vs Minimax")
    print("2. Người vs Random")
    print("3. Minimax vs Random")
    print("4. ML vs Random (cần model)")
    print("5. Minimax vs ML (cần model)")
    print("6. Người vs ML (cần model)")
    
    choice = input("\nNhập lựa chọn (1-6): ").strip()
    
    white_agent = None
    black_agent = None
    human_player = None
    
    if choice == '1':
        human_player = 'white'
        black_agent = MinimaxAgent(depth=3)
    elif choice == '2':
        human_player = 'white'
        black_agent = RandomAgent()
    elif choice == '3':
        white_agent = MinimaxAgent(depth=3)
        black_agent = RandomAgent()
    elif choice == '4':
        white_agent = MLAgent()
        black_agent = RandomAgent()
    elif choice == '5':
        white_agent = MinimaxAgent(depth=3)
        black_agent = MLAgent()
    elif choice == '6':
        human_player = 'white'
        black_agent = MLAgent()
    else:
        print("Lựa chọn không hợp lệ!")
        return
    
    print("\n" + "=" * 60)
    print("BẮT ĐẦU GAME!")
    print("=" * 60)
    
    game = ChessGame(white_agent, black_agent, human_player)
    game.run()


if __name__ == "__main__":
    main()
