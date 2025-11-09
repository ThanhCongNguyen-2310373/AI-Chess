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


### 📁 Cấu trúc thư mục

```
AI-Chess/
├── agents/              # AI agents
├── ml_training/         # ML training notebook
├── data/                # Data
├── models               # Models đã train
├── main.py              # Chạy game
├── evaluate.py          # Đánh giá
├── generate_data.py     # Tạo data
└── test_system.py       # Kiểm tra
```

### 📦 Download ML Model

**File model quá lớn (27MB) nên không đưa vào git.**

**Cách 1: Download từ Google Drive (Khuyến nghị)**
```
1. Mở link: https://drive.google.com/drive/folders/11uqFIv9wt6rTrsMjtNakGkYQ-NhpJ335?usp=sharing
2. Download 2 files:
   - chess_model.h5 (model)
   - normalization_params.npy (de-normalization parameters)
3. Đặt vào: AI-Chess/models/
```

**⚠️ Quan trọng:** Cần CẢ 2 FILES để ML Agent hoạt động chính xác!
- Không có `normalization_params.npy` → ML Agent vẫn chạy nhưng chưa tối ưu

**Cách 2: Train model tự tạo**
```bash
# 1. Generate training data (1000+ games)
python generate_data.py

# 2. Upload data/chess_data.csv lên Google Colab
# 3. Chạy notebook ml_training/train_model.ipynb (đã update)
# 4. Download 2 files về models/:
#    - chess_model.h5
#    - normalization_params.npy
```

###  Yêu cầu

- Python 3.8+
- Các thư viện trong `requirements.txt`


