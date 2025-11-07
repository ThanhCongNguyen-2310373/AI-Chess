"""
Script để tạo dữ liệu training cho ML model
Chạy Minimax tự chơi với chính nó và lưu các trạng thái + điểm số
"""
import chess
import csv
from agents.minimax_agent import MinimaxAgent
from tqdm import tqdm
import random


def generate_game_data(num_games=100, depth=2):
    """
    Tạo dữ liệu từ các ván cờ tự chơi
    
    Args:
        num_games: Số ván cờ
        depth: Độ sâu minimax (dùng depth thấp để nhanh hơn)
    
    Returns:
        List of (fen, score) tuples
    """
    data = []
    agent = MinimaxAgent(depth=depth)
    
    print(f"Tạo dữ liệu từ {num_games} ván cờ...")
    
    for game_num in tqdm(range(num_games)):
        board = chess.Board()
        move_count = 0
        max_moves = 80  # Giới hạn số nước
        
        while not board.is_game_over() and move_count < max_moves:
            # Lưu trạng thái hiện tại
            fen = board.fen()
            score = agent.evaluate_board(board)
            
            data.append((fen, score))
            
            # Agent thực hiện nước đi
            move = agent.get_move(board)
            if move is None:
                break
            
            board.push(move)
            move_count += 1
            
            # Thỉnh thoảng thêm một nước ngẫu nhiên để đa dạng
            if random.random() < 0.1:  # 10% chance
                legal_moves = list(board.legal_moves)
                if legal_moves:
                    random_move = random.choice(legal_moves)
                    board.push(random_move)
                    move_count += 1
    
    print(f"✓ Đã tạo {len(data)} positions")
    return data


def save_to_csv(data, filename='data/chess_data.csv'):
    """
    Lưu dữ liệu vào file CSV
    
    Args:
        data: List of (fen, score)
        filename: Tên file output
    """
    print(f"\nLưu dữ liệu vào {filename}...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['fen', 'score'])  # Header
        writer.writerows(data)
    
    print(f"✓ Đã lưu {len(data)} positions vào {filename}")


def main():
    """Hàm main"""
    print("="*60)
    print("TẠO DỮ LIỆU TRAINING CHO ML MODEL")
    print("="*60)
    
    num_games = int(input("\nNhập số ván cờ (đề xuất: 100-500): ").strip() or "100")
    depth = int(input("Nhập depth cho Minimax (đề xuất: 2): ").strip() or "2")
    
    print("\n" + "="*60)
    
    # Tạo dữ liệu
    data = generate_game_data(num_games=num_games, depth=depth)
    
    # Lưu vào CSV
    save_to_csv(data)
    
    print("\n" + "="*60)
    print("HOÀN TẤT!")
    print("="*60)
    print("\nBước tiếp theo:")
    print("1. Upload file 'data/chess_data.csv' lên Google Colab")
    print("2. Chạy notebook 'ml_training/train_model.ipynb' trên Colab")
    print("3. Download file model về thư mục 'data/'")
    print("="*60)


if __name__ == "__main__":
    # Cài đặt tqdm nếu chưa có
    try:
        from tqdm import tqdm
    except ImportError:
        print("Đang cài đặt tqdm...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'tqdm'])
        from tqdm import tqdm
    
    main()
