# 🎮 AI CHESS - Bài Tập Lớn 2

## Game Playing Agent - Cờ Vua với Minimax và Machine Learning

### 🚀 Bắt đầu nhanh

```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Kiểm tra hệ thống
python test_system.py

# 3. Chơi game
python main.py

# 4. Đánh giá agents
python evaluate.py
```


### ✅ Yêu cầu đề bài

| Yêu cầu | Trạng thái | Tỉ trọng |
|---------|------------|----------|
| Agent đúng luật | ✅ Hoàn thành | Bắt buộc |
| Minimax >= 90% vs Random | ✅ Code sẵn sàng | 75% |
| ML >= 60% vs Random | ✅ Code sẵn sàng | 25% |

### 🤖 Agents

1. **Random Agent** - Baseline
2. **Minimax Agent** - Alpha-Beta Pruning, Evaluation Function
3. **ML Agent** - CNN Neural Network

### 📁 Cấu trúc thư mục

```
AI-Chess/
├── agents/              # AI agents
├── ml_training/         # ML training notebook
├── data/               # Data & models
├── documentation/      # Tài liệu hướng dẫn
├── main.py            # Chạy game
├── evaluate.py        # Đánh giá
├── generate_data.py   # Tạo data
└── test_system.py     # Kiểm tra
```

### � Download ML Model

**File model quá lớn (27MB) nên không đưa vào git.**

**Cách 1: Upload lên Google Drive (Khuyến nghị)**
```
1. Mở link: https://drive.google.com/file/d/11q6N1yLlEqNxfFKiYn7nLudQu3wn7pLd/view?usp=drive_link
2. Download file: chess_model.h5
3. Đặt vào: AI-Chess/models/chess_model.h5
```

**Cách 2: Train model tự tạo**
```bash
# Generate training data (1000 games)
python generate_data.py

# Upload data/chess_data.csv lên Google Colab
# Chạy notebook ml_training/train_model.ipynb
# Download model về models/chess_model.h5
```

### �💻 Yêu cầu

- Python 3.8+
- Các thư viện trong `requirements.txt`


