"""
Script để tạo dữ liệu training cho ML model
Chạy Minimax tự chơi với chính nó và lưu các trạng thái + điểm số
"""
import chess
import csv
from agents.minimax_agent import MinimaxAgent
from tqdm import tqdm
import random


def generate_game_data(num_games=100, depth=2, save_interval=100):
    """
    Tạo dữ liệu từ các ván cờ tự chơi (tối ưu cho số lượng lớn)
    
    Args:
        num_games: Số ván cờ
        depth: Độ sâu minimax (khuyến nghị: 2 cho cân bằng tốc độ/chất lượng)
        save_interval: Lưu file sau mỗi N games (để tránh mất dữ liệu)
    
    Returns:
        List of (fen, score) tuples
    """
    data = []
    agent = MinimaxAgent(depth=depth)
    
    print(f"Tạo dữ liệu từ {num_games} ván cờ (depth={depth})...")
    print(f"Dự kiến: ~{num_games * 40} positions, thời gian: ~{num_games * 30 / 3600:.1f} giờ")
    print(f"Lưu tự động mỗi {save_interval} games để tránh mất dữ liệu\n")
    
    for game_num in tqdm(range(num_games), desc="Generating games"):
        board = chess.Board()
        move_count = 0
        max_moves = 150
        
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
            if random.random() < 0.15:  # 15% chance (tăng để đa dạng hơn)
                legal_moves = list(board.legal_moves)
                if legal_moves and not board.is_game_over():
                    random_move = random.choice(legal_moves)
                    board.push(random_move)
                    move_count += 1
        
        # Lưu định kỳ để tránh mất dữ liệu
        if (game_num + 1) % save_interval == 0:
            save_to_csv(data, filename=f'data/chess_data_backup_{game_num+1}.csv')
            print(f"\n💾 Đã backup {len(data)} positions sau {game_num+1} games")
    
    print(f"\n✓ Đã tạo {len(data)} positions từ {num_games} games")
    print(f"  Trung bình: {len(data)/num_games:.1f} positions/game")
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
    
    print("\n📊 Hướng dẫn chọn số lượng games:")
    print("  - 100 games: ~40 phút, ~4,000 positions (test nhanh)")
    print("  - 500 games: ~4 giờ, ~20,000 positions (khuyến nghị)")
    print("  - 1000 games: ~8 giờ, ~40,000 positions (tốt)")
    print("  - 10000 games: ~80 giờ, ~400,000 positions (rất tốt nhưng lâu!)")
    
    num_games = int(input("\nNhập số ván cờ: ").strip() or "500")
    depth = int(input("Nhập depth cho Minimax (khuyến nghị 2): ").strip() or "2")
    
    # Cảnh báo nếu quá nhiều
    if num_games > 2000:
        confirm = input(f"\n⚠️  {num_games} games sẽ mất ~{num_games*30/3600:.0f} giờ. Tiếp tục? (y/n): ")
        if confirm.lower() != 'y':
            print("Đã hủy.")
            return
    
    print("\n" + "="*60)
    
    # Tạo dữ liệu với auto-save
    save_interval = 100 if num_games >= 1000 else max(50, num_games // 10)
    data = generate_game_data(num_games=num_games, depth=depth, save_interval=save_interval)
    
    # Lưu vào CSV chính
    save_to_csv(data)
    
    print("\n" + "="*60)
    print("✅ HOÀN TẤT!")
    print("="*60)
    print(f"\n📈 Thống kê:")
    print(f"  - Tổng positions: {len(data):,}")
    print(f"  - Trung bình: {len(data)/num_games:.1f} positions/game")
    print(f"  - File: data/chess_data.csv ({len(data) * 100 / 1024:.1f} KB)")
    print("\n🎯 Bước tiếp theo:")
    print("  1. Upload 'data/chess_data.csv' lên Google Colab")
    print("  2. Chạy 'ml_training/train_model.ipynb' để train")
    print("  3. Download model về 'models/chess_model.h5'")
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
