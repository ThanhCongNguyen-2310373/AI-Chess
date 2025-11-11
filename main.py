"""
File chính để chạy game AI Chess
"""
import pygame
import chess
import sys
import time
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
        self.waiting_for_start = True  # Đợi 3s trước khi bắt đầu
        
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
            # Hiển thị "đang suy nghĩ..." trước khi tính toán (ENGLISH)
            self.ui.draw_board(self.board, self.last_move)
            turn_name = "White" if self.board.turn == chess.WHITE else "Black"
            self.ui.draw_info_bar(f"{agent.name} is thinking...", color=(255, 200, 0))
            self.ui.update()
            
            print(f"\n{agent.name} is thinking...")
            
            # KHÔNG lưu FEN của AI (chỉ lưu nước người chơi)
            move = agent.get_move(self.board)
            if move:
                self.board.push(move)
                self.last_move = move
                
                print(f"  → Move: {move.uci()}")
                stats = agent.get_stats()
                print(f"  → Nodes searched: {stats['nodes_searched']}")
    
    def check_game_over(self):
        """Kiểm tra game kết thúc (ENGLISH messages)"""
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            self.result_text = f"{winner} wins by Checkmate!"
            self.game_over = True
        elif self.board.is_stalemate():
            self.result_text = "Draw by Stalemate!"
            self.game_over = True
        elif self.board.is_insufficient_material():
            self.result_text = "Draw by Insufficient Material!"
            self.game_over = True
        elif self.board.is_fifty_moves():
            self.result_text = "Draw by 50-move rule!"
            self.game_over = True
        elif self.board.is_repetition():
            self.result_text = "Draw by Repetition!"
            self.game_over = True
    
    def reset(self):
        """Reset game"""
        self.board.reset()
        self.last_move = None
        self.game_over = False
        self.result_text = ""
        self.ui.clear_history()
        self.waiting_for_start = True  # Reset waiting state
    
    def run(self):
        """Vòng lặp chính của game"""
        running = True
        start_time = time.time()
        
        while running:
            # Đợi 3s trước khi bắt đầu
            if self.waiting_for_start:
                elapsed = time.time() - start_time
                if elapsed < 3.0:
                    # Vẽ countdown
                    self.ui.draw_board(self.board, self.last_move)
                    countdown = int(3 - elapsed) + 1
                    self.ui.draw_info_bar(f"Game starting in {countdown}...", color=(0, 255, 0))
                    self.ui.update()
                    continue
                else:
                    self.waiting_for_start = False
                    print("\n⚔️  GAME STARTED!")
            
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset()
                        start_time = time.time()  # Reset countdown
                    
                    elif event.key == pygame.K_r and not self.game_over:
                        # Toggle pause (đổi từ P sang R)
                        self.ui.toggle_pause()
                    
                    elif event.key == pygame.K_u and not self.game_over and self.human_player:
                        # Undo (chỉ khi có người chơi và không pause)
                        if not self.ui.is_paused and self.ui.can_undo():
                            fen = self.ui.get_undo_state()
                            if fen:
                                self.board.set_fen(fen)
                                self.last_move = None
                                print("\n↶ Undo: Moved back 2 moves")
                
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.ui.is_paused:
                    if self.is_human_turn():
                        move = self.ui.handle_click(self.board, event.pos)
                        if move:
                            # Lưu FEN trước khi đi
                            board_fen_before = self.board.fen()
                            
                            self.board.push(move)
                            self.last_move = move
                            
                            # Lưu vào history
                            self.ui.save_move_for_undo(board_fen_before, move)
                            
                            # VẼ NGAY SAU KHI NGƯỜI CHƠI ĐI
                            self.ui.draw_board(self.board, self.last_move)
                            turn_name = "White" if self.board.turn == chess.WHITE else "Black"
                            self.ui.draw_info_bar(f"{turn_name}'s turn", color=(255, 255, 255))
                            self.ui.update()
                            
                            # Kiểm tra game over sau nước của người
                            self.check_game_over()
            
            # Nếu đang pause, vẽ menu pause
            if self.ui.is_paused:
                self.ui.draw_board(self.board, self.last_move)
                self.ui.draw_pause_menu()
                self.ui.update()
                continue
            
            # AI di chuyển (nếu không phải lượt người)
            if not self.game_over and not self.is_human_turn():
                self.make_ai_move()
            
            # Kiểm tra kết thúc
            self.check_game_over()
            
            # Vẽ giao diện
            self.ui.draw_board(self.board, self.last_move)
            
            # Hiển thị thông tin (ENGLISH)
            if not self.game_over:
                turn_name = "White" if self.board.turn == chess.WHITE else "Black"
                self.ui.draw_info_bar(f"{turn_name}'s turn", color=(255, 255, 255))
            
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
