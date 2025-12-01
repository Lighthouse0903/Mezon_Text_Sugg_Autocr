# Mezon Text Suggestion & Autocorrect  
A lightweight, modular, and extensible Vietnamese text-suggestion + autocorrect engine designed for real-time chatbot UI and typing-assistant environments.

-------------------------------------------------------------------------------

# 1. OVERVIEW  

Mezon Text Suggestion & Autocorrect là hệ thống xử lý tiếng Việt bao gồm:

- Autosuggest: gợi ý từ tiếp theo dựa trên ngữ cảnh và n-gram  
- Autocorrect: sửa lỗi chính tả, lỗi bàn phím, lỗi dấu  
- Normalization: chuẩn hóa Unicode tiếng Việt, xử lý teencode  
- Candidate generation: sinh từ ứng viên dựa trên edit distance + keyboard distance  
- Language Model: unigram, bigram, trigram  
- Realtime engine: xử lý khi người dùng nhập từng ký tự  
- Mezon Bot integration: UI + API phục vụ chat realtime  

Dự án được chia thành các module chính:

- Python Engine (src/)  
- Autocorrect & Autosuggest modules  
- Data pipeline phục vụ training  
- Realtime Node.js integration (mezon_bot/)  
- Notebooks phân tích thử nghiệm  

-------------------------------------------------------------------------------

# 2. FEATURES

## Autocorrect Engine  
- Sửa lỗi gõ sai dấu, thiếu dấu  
- Sửa lỗi gõ nhầm phím theo keyboard distance  
- Chuẩn hóa Unicode (NFC/NFD)  
- Xử lý teencode → tiếng Việt chuẩn  
- Context-based correction  
- Candidate ranking dựa vào n-gram  

## Autosuggest Engine  
- N-gram language model (2-gram, 3-gram)  
- Dự đoán từ tiếp theo theo xác suất  
- Candidate ranking  
- Hỗ trợ chạy realtime  

## Realtime Support  
- Autocorrect realtime engine (Python)  
- Node.js Web/API realtime  
- Tối ưu tốc độ cho UI chatbot  

## Data Pipeline  
- Làm sạch corpus  
- Sinh noisy data  
- Tạo vocab  
- Split dataset train/val/test  
- Training scripts đầy đủ  

-------------------------------------------------------------------------------

# 3. PROJECT STRUCTURE

Mezon_Text_Sugg_Autocr/  
│  
├── mezon_bot/  
│   ├── api/                           API backend kết nối Python ↔ Node.js  
│   ├── node_modules/                  Dependencies Node.js  
│   ├── ui/                            UI demo realtime  
│   ├── bot_keyboard.js                Xử lý sự kiện bàn phím  
│   ├── bot_test.js                    Test bot qua terminal  
│   ├── index.js                       Server + UI + API bridge  
│   ├── package.json                   Metadata + dependencies  
│   └── package-lock.json              Lock version  
│  
├── notebooks/  
│   └── *.ipynb                        Notebook phân tích, trực quan, test mô hình  
│  
├── src/  
│   ├── autocorrect/  
│   │   ├── core/  
│   │   │   ├── context_corrector.py     Sửa lỗi theo ngữ cảnh  
│   │   │   ├── demo_realtime.py         Demo realtime trong terminal  
│   │   │   ├── generate_candidate.py    Sinh từ ứng viên  
│   │   │   ├── hard_rules.py            Teencode/viết tắt rules  
│   │   │   ├── keyboard_fix.py          Sửa lỗi gõ nhầm phím  
│   │   │   ├── normalize_vi.py          Chuẩn hóa Unicode  
│   │   │   ├── rank_candidates.py       Chấm điểm ứng viên  
│   │   │   └── realtime.py              Autocorrect realtime engine  
│   │   │  
│   │   ├── data/  
│   │   │   ├── analyze_pairs.py         Phân tích cặp sai - đúng  
│   │   │   ├── build_vocab.py           Tạo từ điển  
│   │   │   ├── clean_external_corpus.py Làm sạch corpus thô  
│   │   │   ├── filter_pairs.py          Lọc tập cặp từ  
│   │   │   ├── filter_pairs_by_distance.py Lọc thêm theo edit distance  
│   │   │   └── split_dataset.py         Tách train/val/test  
│   │   │  
│   │   └── scripts/  
│   │       ├── autocorrect_model.py     Train autocorrect  
│   │       └── infer.py                 Chạy autocorrect qua terminal  
│   │  
│   ├── autosuggest/  
│   │   ├── data/  
│   │   │   ├── clean_corpus.py          Làm sạch corpus  
│   │   │   ├── generate_noisy_pairs.py  Sinh noisy data  
│   │   │   └── split.py                 Tách dataset  
│   │   │  
│   │   ├── eval/  
│   │   │   ├── quick_eval.py            Đánh giá nhanh  
│   │   │   └── test_model.py            Test accuracy  
│   │   │  
│   │   ├── lm/  
│   │   │   └── ngram.py                 Mô hình n-gram  
│   │   │  
│   │   └── scripts/  
│   │       └── train_ngram.py           Train n-gram  
│  
├── requirements.txt                    Danh sách dependencies Python  
└── .gitignore                          File ignore của toàn project  

-------------------------------------------------------------------------------

# 4. INSTALLATION (FAST SETUP)

$ git clone https://github.com/Lighthouse0903/Mezon_Text_Sugg_Autocr.git  
$ cd Mezon_Text_Sugg_Autocr  

Tạo virtual environment:  
$ python -m venv .venv  

Kích hoạt môi trường ảo:  
Windows:  
$ .venv\Scripts\activate  
Linux/macOS:  
$ source .venv/bin/activate  

Cài đặt thư viện:  
$ pip install -r requirements.txt  

-------------------------------------------------------------------------------

# 5. TUTORIAL — HƯỚNG DẪN SỬ DỤNG

## 1. Chạy autocorrect cơ bản  
$ python src/autocorrect/scripts/infer.py --text "hom nay toi di choi"  

## 2. Demo autocorrect realtime  
$ python src/autocorrect/core/demo_realtime.py  

## 3. Chạy autosuggest  
$ python src/autosuggest/eval/test_model.py  

## 4. Training autosuggest  
$ python src/autosuggest/data/clean_corpus.py  
$ python src/autosuggest/data/generate_noisy_pairs.py  
$ python src/autosuggest/scripts/train_ngram.py  

## 5. Training autocorrect  
$ python src/autocorrect/data/clean_external_corpus.py  
$ python src/autocorrect/data/build_vocab.py  
$ python src/autocorrect/data/analyze_pairs.py  
$ python src/autocorrect/data/filter_pairs.py  
$ python src/autocorrect/scripts/autocorrect_model.py  

-------------------------------------------------------------------------------

# 6. MEZON BOT INTEGRATION (NODE.JS)

Cài dependencies Node.js:  
$ cd mezon_bot  
$ npm install  

Chạy bot server:  
$ node index.js  

Test nhanh bằng terminal:  
$ node bot_test.js  

UI realtime (mở trình duyệt):  
http://localhost:3000  

-------------------------------------------------------------------------------

# 7. TUỲ CHỈNH CẤU HÌNH

Autocorrect top-k:  
TOP_K = 5  

N-gram context length:  
N = 3  

Rule sửa phím:  
keyboard_fix.py  

Rule teencode:  
hard_rules.py  

-------------------------------------------------------------------------------

# 8. LỖI THƯỜNG GẶP

Thiếu dependencies Python:  
$ pip install -r requirements.txt  

Node.js không chạy:  
$ npm install  

Lỗi Unicode:  
$ python src/autocorrect/core/normalize_vi.py  

-------------------------------------------------------------------------------

# 9. HOÀN TẤT  
README này đã bao gồm đầy đủ:  
- Overview  
- Features  
- Project Structure  
- Installation  
- Tutorial  
- Bot integration  
- Config  
- Troubleshooting  

# Video Demo
[![Watch the demo](https://raw.githubusercontent.com/Lighthouse0903/Mezon_Text_Sugg_Autocr/master/thumbnail.png)](https://github.com/Lighthouse0903/Mezon_Text_Sugg_Autocr/releases/download/v1.0.0/Demo.mp4)
