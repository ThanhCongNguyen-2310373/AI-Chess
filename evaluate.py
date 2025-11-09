"""
Script để đánh giá hiệu suất của các agents
Chạy nhiều ván và tính tỉ lệ thắng
"""
import chess
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.ml_agent import MLAgent
import time


def play_game(white_agent, black_agent, max_moves=200, verbose=False):
    """
    Chơi một ván cờ giữa 2 agents
    
    Args:
        white_agent: Agent chơi quân trắng
        black_agent: Agent chơi quân đen
        max_moves: Số nước tối đa (tránh game vô tận)
        verbose: In thông tin chi tiết
    
    Returns:
        'white': Trắng thắng
        'black': Đen thắng
        'draw': Hòa
    """
    board = chess.Board()
    move_count = 0
    
    while not board.is_game_over() and move_count < max_moves:
        # Lấy agent hiện tại
        if board.turn == chess.WHITE:
            agent = white_agent
        else:
            agent = black_agent
        
        # Lấy nước đi
        move = agent.get_move(board)
        
        if move is None:
            break
        
        # Thực hiện nước đi
        board.push(move)
        move_count += 1
        
        if verbose:
            print(f"Move {move_count}: {move.uci()}")
    
    # Xác định kết quả
    if board.is_checkmate():
        if board.turn == chess.BLACK:
            return 'white'
        else:
            return 'black'
    else:
        return 'draw'


def evaluate_agent(agent, opponent, num_games=100, agent_color='white'):
    """
    Đánh giá agent bằng cách chơi nhiều ván với opponent
    
    Args:
        agent: Agent cần đánh giá
        opponent: Agent đối thủ
        num_games: Số ván chơi
        agent_color: Màu của agent ('white' hoặc 'black')
    
    Returns:
        Dict chứa kết quả
    """
    print(f"\n{'='*60}")
    print(f"ĐÁNH GIÁ: {agent.name} vs {opponent.name}")
    print(f"Agent màu: {agent_color.upper()}")
    print(f"Số ván: {num_games}")
    print(f"{'='*60}\n")
    
    wins = 0
    losses = 0
    draws = 0
    
    start_time = time.time()
    
    for i in range(num_games):
        print(f"Ván {i+1}/{num_games}...", end=" ")
        
        if agent_color == 'white':
            result = play_game(agent, opponent)
            if result == 'white':
                wins += 1
                print("✓ THẮNG")
            elif result == 'black':
                losses += 1
                print("✗ THUA")
            else:
                draws += 1
                print("= HÒA")
        else:
            result = play_game(opponent, agent)
            if result == 'black':
                wins += 1
                print("✓ THẮNG")
            elif result == 'white':
                losses += 1
                print("✗ THUA")
            else:
                draws += 1
                print("= HÒA")
    
    elapsed_time = time.time() - start_time
    
    # Tính tỉ lệ
    win_rate = (wins / num_games) * 100
    loss_rate = (losses / num_games) * 100
    draw_rate = (draws / num_games) * 100
    
    # In kết quả
    print(f"\n{'='*60}")
    print("KẾT QUẢ:")
    print(f"  Thắng: {wins}/{num_games} ({win_rate:.1f}%)")
    print(f"  Thua:  {losses}/{num_games} ({loss_rate:.1f}%)")
    print(f"  Hòa:   {draws}/{num_games} ({draw_rate:.1f}%)")
    print(f"  Thời gian: {elapsed_time:.2f}s")
    print(f"  TB/ván: {elapsed_time/num_games:.2f}s")
    print(f"{'='*60}\n")
    
    return {
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': win_rate,
        'loss_rate': loss_rate,
        'draw_rate': draw_rate,
        'total_time': elapsed_time,
        'avg_time_per_game': elapsed_time / num_games
    }


def main():
    """Hàm main để đánh giá"""
    print("\n" + "="*60)
    print("ĐÁNH GIÁ HIỆU SUẤT AGENTS")
    print("="*60)
    
    # Tạo các agents
    print("\nKhởi tạo agents...")
    random_agent = RandomAgent()
    minimax_agent = MinimaxAgent(depth=3)
    
    print("✓ Random Agent")
    print("✓ Minimax Agent")
    
    # Đánh giá Minimax vs Random
    print("\n" + "="*60)
    print("YÊU CẦU: Minimax phải thắng Random >= 90%")
    print("="*60)
    
    num_games = int(input("\nNhập số ván để test (đề xuất: 20-50): ").strip() or "20")
    
    # Test Minimax màu trắng
    result_white = evaluate_agent(minimax_agent, random_agent, 
                                   num_games=num_games, agent_color='white')
    
    # Test Minimax màu đen
    result_black = evaluate_agent(minimax_agent, random_agent, 
                                   num_games=num_games, agent_color='black')
    
    # Tổng kết
    total_wins = result_white['wins'] + result_black['wins']
    total_games = num_games * 2
    overall_win_rate = (total_wins / total_games) * 100
    
    print("\n" + "="*60)
    print("TỔNG KẾT MINIMAX")
    print("="*60)
    print(f"Tổng số ván: {total_games}")
    print(f"Tổng thắng: {total_wins}")
    print(f"Tỉ lệ thắng: {overall_win_rate:.1f}%")
    
    if overall_win_rate >= 90:
        print("✓✓✓ ĐẠT YÊU CẦU (>= 90%)")
    else:
        print(f"✗✗✗ CHƯA ĐẠT (cần >= 90%, hiện tại: {overall_win_rate:.1f}%)")
        print("    → Cần tăng depth hoặc cải thiện evaluation function")
    
    print("="*60)
    
    # Test ML agent nếu có
    try:
        print("\n" + "="*60)
        print("YÊU CẦU: ML Agent phải thắng Random >= 60%")
        print("="*60)
        
        ml_agent = MLAgent()
        
        if ml_agent.model is not None:
            result_ml_white = evaluate_agent(ml_agent, random_agent, 
                                            num_games=num_games, agent_color='white')
            
            result_ml_black = evaluate_agent(ml_agent, random_agent, 
                                            num_games=num_games, agent_color='black')
            
            total_ml_wins = result_ml_white['wins'] + result_ml_black['wins']
            ml_win_rate = (total_ml_wins / total_games) * 100
            
            print("\n" + "="*60)
            print("TỔNG KẾT ML AGENT")
            print("="*60)
            print(f"Tổng số ván: {total_games}")
            print(f"Tổng thắng: {total_ml_wins}")
            print(f"Tỉ lệ thắng: {ml_win_rate:.1f}%")
            
            if ml_win_rate >= 60:
                print("✓✓✓ ĐẠT YÊU CẦU (>= 60%)")
            else:
                print(f"✗✗✗ CHƯA ĐẠT (cần >= 60%, hiện tại: {ml_win_rate:.1f}%)")
                print("    → Cần train thêm hoặc cải thiện model")
            
            print("="*60)
        else:
            print("\n⚠ Chưa có ML model, bỏ qua đánh giá ML Agent")
            print("  → Hãy train model bằng script generate_data.py và train_model.ipynb")
    
    except Exception as e:
        print(f"\n⚠ Lỗi khi test ML Agent: {e}")


if __name__ == "__main__":
    main()
