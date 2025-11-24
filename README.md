# Mezon Text Suggestion & Autocorrect  
A lightweight, modular, and extensible text-suggestion + autocorrect engine for Vietnamese input, designed for real-time usage inside chatbots or UI typing environments.

---

##  Overview  
**Mezon Text Suggestion & Autocorrect** là dự án xử lý ngôn ngữ tự nhiên (NLP) dùng để:

- Gợi ý từ (autosuggest)
- Sửa lỗi chính tả theo ngữ cảnh (autocorrect)
- Chuẩn hoá văn bản tiếng Việt (remove dấu lỗi, fix teencode, normalize Unicode)
- Đưa ra các candidate từ/tổ hợp câu phù hợp dựa vào corpus + thuật toán n-gram
- Chạy **real-time** trong giao diện chatbot Mezon // Inprogess

Dự án được chia thành nhiều mô-đun rõ ràng:  
- Engine chính (`src/`)
- Module autosuggest + autocorrect
- Bộ tiền xử lý dữ liệu, training corpus  
- Real-time API/UI tích hợp vào Mezon bot (`mezon_bot/`)
- Notebook phân tích thử nghiệm (`notebooks/`)

---

## Features  
### Autocorrect Engine  
- Sửa lỗi gõ sai dấu, thiếu dấu  
- Sửa lỗi gõ nhầm phím (keyboard distance rules)  
- Sửa lỗi ghép từ không hợp lệ  
- Thay thế teencode / viết tắt sang văn bản nghiêm túc  
- Normalization tiếng Việt (NFC/NFD, chuẩn hoá Unicode)

### Autosuggest Engine  
- Gợi ý từ dựa trên n-gram (2-gram, 3-gram)  
- Tạo danh sách candidate theo frequency từ corpus  
- Ranking candidates theo score + context window  
- Gợi ý thời gian thực khi người dùng đang nhập

### Real-time Support  
- Module `realtime.py` chạy gợi ý tức thì (suitable for chatbot UI)  
- Tối ưu performance để không bị trễ khi người dùng đang gõ  

### Data Pipeline  
- Làm sạch corpus  
- Tạo cặp noisy data → training autocorrect  
- Sinh vocab + thống kê n-gram  
- Split dataset phục vụ test/eval  

---

## Project Structure  
Cấu trúc repo dựa trên source bạn cung cấp:
Mezon_Text_Sugg_Autocr/
├── mezon_bot/
│   ├── api/                          # API backend phục vụ bot (HTTP/WebSocket)
│   ├── node_modules/                 # Dependencies Node.js
│   ├── ui/                           # Giao diện/UI cho bot hoặc demo typing
│   ├── bot_keyboard.js               # Logic xử lý gõ phím trong UI bot (keyup/keydown events)
│   ├── bot_test.js                   # Script test bot, gửi input → nhận gợi ý để kiểm tra nhanh
│   ├── index.js                      # Entry point chính của bot (khởi chạy server, load API)
│   ├── package.json                  # Metadata + dependencies cho Node.js bot
│   └── package-lock.json             # Lock dependency (đảm bảo version cố định)
│
├── notebooks/
│   └── *.ipynb                       # Jupyter notebooks 
│
├── src/
│   ├── autocorrect/
│   │   ├── core/
│   │   │   ├── context_corrector.py  # Sửa lỗi dựa vào ngữ cảnh câu (context-based correction)
│   │   │   ├── demo_realtime.py      # Demo real-time autocorrect chạy trên terminal
│   │   │   ├── generate_candidate.py # Sinh danh sách từ candidate dựa vào:
│   │   │   │                         # edit distance, keyboard distance, heuristic rules
│   │   │   ├── hard_rules.py         # Các luật cứng: teencode → tiếng Việt chuẩn, fix viết tắt
│   │   │   ├── keyboard_fix.py       # Sửa lỗi gõ nhầm phím (bấm phím cạnh nhau)
│   │   │   ├── normalize_vi.py       # Chuẩn hóa Unicode tiếng Việt (NFC/NFD)
│   │   │   ├── rank_candidates.py    # Xếp hạng candidate theo điểm n-gram + context score
│   │   │   └── realtime.py           # Engine chạy autocorrect thời gian thực
│   │   │
│   │   ├── data/
│   │   │   ├── analyze_pairs.py      # Phân tích cặp từ đúng–sai trong dataset
│   │   │   ├── build_vocab.py        # Tạo vocab (từ điển) từ corpus sạch
│   │   │   ├── clean_external_corpus.py# Làm sạch corpus dạng thô (remove ký tự lỗi)
│   │   │   ├── filter_pairs.py       # Lọc dataset các cặp từ sai–đúng
│   │   │   ├── filter_pairs_by_distance.py # Lọc thêm theo edit distance cho training
│   │   │   └── split_dataset.py      # Tách dataset thành train/val/test
│   │   │
│   │   └── scripts/
│   │       ├── autocorrect_model.py  # Mô hình autocorrect (training hoặc load model)
│   │       └── infer.py              # Script thực thi autocorrect với input dòng lệnh
│   │
│   ├── autosuggest/
│   │   ├── data/
│   │   │   ├── clean_corpus.py       # Làm sạch văn bản → dùng cho n-gram training
│   │   │   ├── generate_noisy_pairs.py# Tạo dữ liệu nhiễu để kiểm tra autosuggest
│   │   │   └── split.py              # Tách dữ liệu autosuggest thành train/test
│   │   │
│   │   ├── eval/
│   │   │   ├── quick_eval.py         # Đánh giá nhanh chất lượng gợi ý
│   │   │   └── test_model.py         # Test accuracy autosuggest với dataset
│   │   │
│   │   ├── lm/
│   │   │   └── ngram.py              # Mô hình n-gram (unigram/bigram/trigram)
│   │   │                             # tính xác suất từ tiếp theo
│   │   │
│   │   └── scripts/
│   │       └── train_ngram.py        # Script huấn luyện n-gram model từ corpus
│   │
│   ├── requirements.txt              # Dependencies Python của toàn project
│   └── .gitignore                    # Ignore file không cần commit
│
└── .venv/                             # (Không commit) Virtual environment Python

# TUTORIAL — HƯỚNG DẪN SỬ DỤNG DỰ ÁN

## 1. SETUP MÔI TRƯỜNG

### 1. Clone dự án về máy
Lệnh tải mã nguồn từ GitHub:
$ git clone https://github.com/Lighthouse0903/Mezon_Text_Sugg_Autocr.git
$ cd Mezon_Text_Sugg_Autocr

### 2. Tạo môi trường ảo Python (virtual environment)
Tạo môi trường độc lập để tránh xung đột thư viện:
$ python -m venv .venv

### 3. Kích hoạt môi trường ảo
Windows:
$ .venv\Scripts\activate

macOS/Linux:
$ source .venv/bin/activate

### 4. Cài đặt dependencies
$ pip install -r requirements.txt


## 2. CHẠY AUTOCORRECT CƠ BẢN

Autocorrect giúp sửa lỗi chính tả, lỗi bàn phím và lỗi dấu tiếng Việt.

### Chạy thử chức năng sửa lỗi:
$ python src/autocorrect/scripts/infer.py --text "hom nay toi di choi"

Kết quả mong đợi:
"hôm nay tôi đi chơi"


## 3. DEMO AUTOCORRECT REALTIME

Chế độ real-time xử lý từng ký tự nhập vào và đưa ra gợi ý tức thì.

Chạy demo:
$ python src/autocorrect/core/demo_realtime.py


## 4. CHẠY AUTOSUGGEST (GỢI Ý TỪ TIẾP THEO)

Autosuggest dự đoán từ tiếp theo dựa trên mô hình N-gram.

Chạy test autosuggest:
$ python src/autosuggest/eval/test_model.py


## 5. HUẤN LUYỆN AUTOSUGGEST (N-GRAM MODEL)

### 1. Làm sạch corpus:
$ python src/autosuggest/data/clean_corpus.py

### 2. Tạo noisy pairs:
$ python src/autosuggest/data/generate_noisy_pairs.py

### 3. Huấn luyện mô hình:
$ python src/autosuggest/scripts/train_ngram.py


## 6. HUẤN LUYỆN AUTOCORRECT MODEL

Autocorrect sử dụng nhiều rule kết hợp dữ liệu huấn luyện sai → đúng.

### 1. Làm sạch dữ liệu:
$ python src/autocorrect/data/clean_external_corpus.py

### 2. Xây dựng từ điển:
$ python src/autocorrect/data/build_vocab.py

### 3. Phân tích và lọc cặp từ sai/đúng:
$ python src/autocorrect/data/analyze_pairs.py
$ python src/autocorrect/data/filter_pairs.py

### 4. Train mô hình:
$ python src/autocorrect/scripts/autocorrect_model.py


## 7. TÍCH HỢP VỚI MEZON BOT (NODE.JS)

### 1. Cài dependencies:
$ cd mezon_bot
$ npm install

### 2. Chạy bot:
$ node index.js

### 3. Test bot:
$ node bot_test.js


## 8. UI DEMO

UI demo được xây dựng bằng Node.js.

Chạy UI:
$ node index.js

Truy cập:
http://localhost:3000


## 9. TUỲ CHỈNH CẤU HÌNH

Số lượng gợi ý trả về:
TOP_K = 5

Độ dài n-gram:
N = 3

Điều chỉnh rules sửa bàn phím:
keyboard_fix.py

Điều chỉnh rules teencode:
hard_rules.py


## 10. LỖI THƯỜNG GẶP

Thiếu thư viện Python:
$ pip install -r requirements.txt

Bot Node.js không chạy:
$ npm install

Lỗi Unicode tiếng Việt:
$ python src/autocorrect/core/normalize_vi.py

## HOÀN TẤT
