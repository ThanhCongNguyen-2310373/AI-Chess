"""
Script kiểm tra toàn bộ hệ thống
Chạy file này để đảm bảo mọi thứ hoạt động
"""
import sys
import os

def test_imports():
    """Kiểm tra import các thư viện"""
    print("="*60)
    print("KIỂM TRA THƯ VIỆN")
    print("="*60)
    
    tests = [
        ("chess", "python-chess"),
        ("pygame", "pygame"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
    ]
    
    all_ok = True
    for module, package in tests:
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - Chưa cài đặt")
            print(f"  Chạy: pip install {package}")
            all_ok = False
    
    # TensorFlow (optional)
    try:
        import tensorflow
        print(f"✓ tensorflow")
    except ImportError:
        print(f"⚠ tensorflow - Chưa cài (cần cho ML Agent)")
        print(f"  Chạy: pip install tensorflow")
    
    return all_ok


def test_agents():
    """Kiểm tra các agents hoạt động"""
    print("\n" + "="*60)
    print("KIỂM TRA AGENTS")
    print("="*60)
    
    try:
        import chess
        from agents.random_agent import RandomAgent
        from agents.minimax_agent import MinimaxAgent
        
        board = chess.Board()
        
        # Test Random Agent
        print("\nTest Random Agent...", end=" ")
        random_agent = RandomAgent()
        move = random_agent.get_move(board)
        assert move is not None
        assert move in board.legal_moves
        print("✓")
        
        # Test Minimax Agent
        print("Test Minimax Agent (depth=2)...", end=" ")
        minimax_agent = MinimaxAgent(depth=2)
        move = minimax_agent.get_move(board)
        assert move is not None
        assert move in board.legal_moves
        stats = minimax_agent.get_stats()
        assert stats['nodes_searched'] > 0
        print(f"✓ (searched {stats['nodes_searched']} nodes)")
        
        # Test ML Agent (if model exists)
        print("Test ML Agent...", end=" ")
        try:
            from agents.ml_agent import MLAgent
            ml_agent = MLAgent()
            if ml_agent.model is not None:
                move = ml_agent.get_move(board)
                assert move is not None
                print("✓ (model loaded)")
            else:
                print("⚠ (no model, using random)")
        except Exception as e:
            print(f"⚠ (error: {e})")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Kiểm tra các hàm utils"""
    print("\n" + "="*60)
    print("KIỂM TRA UTILS")
    print("="*60)
    
    try:
        import chess
        import numpy as np
        from utils import (
            get_piece_value, 
            get_position_value, 
            fen_to_tensor,
            is_endgame
        )
        
        board = chess.Board()
        
        # Test get_piece_value
        print("\nTest get_piece_value...", end=" ")
        pawn = chess.Piece(chess.PAWN, chess.WHITE)
        queen = chess.Piece(chess.QUEEN, chess.WHITE)
        assert get_piece_value(pawn) == 100
        assert get_piece_value(queen) == 900
        print("✓")
        
        # Test fen_to_tensor
        print("Test fen_to_tensor...", end=" ")
        fen = board.fen()
        tensor = fen_to_tensor(fen)
        assert tensor.shape == (8, 8, 12)
        assert tensor.sum() == 32  # 32 quân cờ
        print("✓")
        
        # Test is_endgame
        print("Test is_endgame...", end=" ")
        assert not is_endgame(board)  # Vị trí đầu không phải endgame
        print("✓")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_game_logic():
    """Kiểm tra logic game"""
    print("\n" + "="*60)
    print("KIỂM TRA GAME LOGIC")
    print("="*60)
    
    try:
        import chess
        from agents.minimax_agent import MinimaxAgent
        from agents.random_agent import RandomAgent
        
        print("\nChạy 1 ván Minimax vs Random...", end=" ")
        
        board = chess.Board()
        white = MinimaxAgent(depth=2)
        black = RandomAgent()
        
        moves = 0
        max_moves = 50
        
        while not board.is_game_over() and moves < max_moves:
            if board.turn == chess.WHITE:
                move = white.get_move(board)
            else:
                move = black.get_move(board)
            
            if move is None:
                break
            
            board.push(move)
            moves += 1
        
        print(f"✓ ({moves} nước đi)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_files():
    """Kiểm tra các file cần thiết"""
    print("\n" + "="*60)
    print("KIỂM TRA CẤU TRÚC FILES")
    print("="*60)
    
    required_files = [
        "main.py",
        "evaluate.py",
        "generate_data.py",
        "config.py",
        "utils.py",
        "game_ui.py",
        "agents/__init__.py",
        "agents/base_agent.py",
        "agents/random_agent.py",
        "agents/minimax_agent.py",
        "agents/ml_agent.py",
        "ml_training/train_model.ipynb",
        "README.md",
        "requirements.txt"
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - Thiếu file")
            all_ok = False
    
    # Check optional files
    optional_files = [
        ("data/chess_data.csv", "Dữ liệu training"),
        ("data/chess_model.h5", "ML model")
    ]
    
    print("\nFiles tùy chọn:")
    for file, desc in optional_files:
        if os.path.exists(file):
            print(f"✓ {file} - {desc}")
        else:
            print(f"⚠ {file} - {desc} (chưa có)")
    
    return all_ok


def main():
    """Chạy tất cả tests"""
    print("\n" + "="*60)
    print("KIỂM TRA TOÀN BỘ HỆ THỐNG")
    print("="*60)
    
    results = []
    
    # Test imports
    results.append(("Thư viện", test_imports()))
    
    # Test files
    results.append(("Cấu trúc files", test_files()))
    
    # Test utils
    results.append(("Utils", test_utils()))
    
    # Test agents
    results.append(("Agents", test_agents()))
    
    # Test game logic
    results.append(("Game logic", test_game_logic()))
    
    # Summary
    print("\n" + "="*60)
    print("TỔNG KẾT")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 TẤT CẢ TEST ĐỀU PASS!")
        print("\nHệ thống sẵn sàng sử dụng:")
        print("  - Chạy game: python main.py")
        print("  - Đánh giá: python evaluate.py")
        print("  - Tạo data: python generate_data.py")
    else:
        print("\n⚠ MỘT SỐ TEST FAILED")
        print("\nVui lòng kiểm tra lại:")
        print("  1. Cài đặt đủ thư viện: pip install -r requirements.txt")
        print("  2. Kiểm tra code có lỗi syntax không")
        print("  3. Đọc hướng dẫn trong README.md")
    
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
