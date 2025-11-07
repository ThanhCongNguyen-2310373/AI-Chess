"""
Test ML Agent - Kiểm tra xem model có hoạt động không
"""
import chess
from agents.ml_agent import MLAgent
from agents.random_agent import RandomAgent
import time

def test_ml_agent():
    """Test xem ML agent có load được model và chơi được không"""
    print("="*60)
    print("TEST ML AGENT")
    print("="*60)
    
    try:
        # Khởi tạo ML agent
        print("\n1. Đang load model...")
        ml_agent = MLAgent()
        print("   ✓ Load model thành công!")
        
        # Test trên vị trí bắt đầu
        print("\n2. Test đánh giá vị trí bắt đầu...")
        board = chess.Board()
        score = ml_agent.evaluate_board(board)
        print(f"   Score: {score:.2f}")
        print("   (Nên gần 0 vì vị trí cân bằng)")
        
        # Test chọn nước đi
        print("\n3. Test chọn nước đi...")
        move = ml_agent.get_move(board)
        print(f"   Nước đi: {move}")
        print(f"   ✓ ML agent hoạt động bình thường!")
        
        # Test chơi vài nước
        print("\n4. Test chơi 5 nước đi...")
        for i in range(5):
            if board.is_game_over():
                break
            move = ml_agent.get_move(board)
            if move:
                board.push(move)
                print(f"   Nước {i+1}: {move} (Score: {ml_agent.evaluate_board(board):.2f})")
        
        print("\n" + "="*60)
        print("✓ ML AGENT HOẠT ĐỘNG TỐT!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ LỖI: {e}")
        print("\nKiểm tra:")
        print("1. File 'models/chess_model.h5' có tồn tại không?")
        print("2. TensorFlow đã cài đặt chưa? (pip install tensorflow)")
        print("="*60)
        return False


def test_ml_vs_random(num_games=5):
    """Test ML agent vs Random agent"""
    print("\n" + "="*60)
    print(f"TEST: ML AGENT vs RANDOM ({num_games} ván)")
    print("="*60)
    
    try:
        ml_agent = MLAgent()
        random_agent = RandomAgent()
        
        ml_wins = 0
        random_wins = 0
        draws = 0
        
        for game_num in range(num_games):
            print(f"\nVán {game_num + 1}/{num_games}...", end=" ")
            board = chess.Board()
            move_count = 0
            max_moves = 100
            
            while not board.is_game_over() and move_count < max_moves:
                # ML chơi trắng, Random chơi đen
                if board.turn == chess.WHITE:
                    move = ml_agent.get_move(board)
                else:
                    move = random_agent.get_move(board)
                
                if move:
                    board.push(move)
                    move_count += 1
                else:
                    break
            
            # Kết quả
            result = board.result()
            if result == "1-0":
                ml_wins += 1
                print("ML thắng!")
            elif result == "0-1":
                random_wins += 1
                print("Random thắng!")
            else:
                draws += 1
                print("Hòa!")
        
        print("\n" + "="*60)
        print("KẾT QUẢ:")
        print(f"  ML wins:     {ml_wins}/{num_games} ({ml_wins/num_games*100:.1f}%)")
        print(f"  Random wins: {random_wins}/{num_games} ({random_wins/num_games*100:.1f}%)")
        print(f"  Draws:       {draws}/{num_games} ({draws/num_games*100:.1f}%)")
        
        win_rate = ml_wins / num_games * 100
        if win_rate >= 60:
            print(f"\n✓ ĐẠT YÊU CẦU! (>= 60%)")
        else:
            print(f"\n✗ CHƯA ĐẠT YÊU CẦU (<60%)")
            print("\nGợi ý cải thiện:")
            print("1. Train với nhiều dữ liệu hơn (500-1000 ván)")
            print("2. Tăng depth khi generate data (depth=3)")
            print("3. Train lâu hơn (50-100 epochs)")
        
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ LỖI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Test cơ bản
    if test_ml_agent():
        # Nếu test cơ bản pass, test đấu với Random
        print("\n")
        test_ml_vs_random(num_games=5)
